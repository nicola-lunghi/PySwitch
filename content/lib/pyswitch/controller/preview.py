from ..misc import PeriodCounter, Colors

# Handler which controle the DisplayLabel override_text mechanisms for usage 
# as value preview or similar things. It handles the blinking and timeouts etc.
class ValuePreview:

    __labels = {}

    # There is only one ValuePreview handler for each label
    @staticmethod
    def get(label,
            timeout_millis = None,
            blink_interval_millis = None,
            blink_color = Colors.WHITE
        ):

        if not label in ValuePreview.__labels:            
            ValuePreview.__labels[label] = ValuePreview(
                create_key = ValuePreview,
                label = label,
                timeout_millis = timeout_millis,
                blink_interval_millis = blink_interval_millis,
                blink_color = blink_color
            )

        return ValuePreview.__labels[label]

    ###################################################################################################

    def __init__(self,
                 create_key,
                 label,
                 timeout_millis,
                 blink_interval_millis,
                 blink_color,
        ):
        if create_key != ValuePreview:
            raise Exception()   # Private constructor
        
        self.label = label

        self.__period = PeriodCounter(timeout_millis) if timeout_millis else None

        self.__blink = False
        self.__stay = False
        self.__blink_period = PeriodCounter(blink_interval_millis) if blink_interval_millis else None
        self.__blink_state = False
        self.__orig_color = label.text_color
        self.__blink_color = blink_color

        self.__clients = [] # List of clients to be canceled when another client enters. Each one must have a cancel() method.

    # Sets a preview (override) text on the label. This text will:
    # - Blink before being reset (if blink is True)
    # - Stay until reset is called (stay = True) or disappear after the timeout interval (stay = False)
    #
    # Inf a client is given, it must have a cancel() method which will be called when someone else enters preview.
    def preview(self, text, blink = False, stay = False, client = None):
        for c in self.__clients:
            if c == client:
                continue

            c.cancel()

        self.label.override_text = text
        self.label.update_label()

        if self.__period:
            self.__period.reset()
        
        self.__stay = stay

        if not self.__blink and blink and self.__blink_period:
            self.__blink_period.reset()

        self.__blink = blink

        if client and not client in self.__clients:
            self.__clients.append(client)
        
    # Preview a mapping value (percentage)
    def preview_mapping(self, value, mapping, max_value, blink = False, stay = False, client = None):
        prefix = f"{ mapping.name }: " if mapping.name else ""
        val = round(value * 100 / max_value)
        
        self.preview(
            text = f"{ prefix }{ str(val) }%",
            blink = blink,
            stay = stay,
            client = client
        )        

    # Reset the display label to its default behaviour, either immediately or after the timeout period.
    def reset(self, immediately = False):
        self.__blink = False
        self.__stay = False

        self.label.text_color = self.__orig_color

        if immediately:
            self.label.override_text = None
            self.label.update_label()

        elif self.__period:
            self.__period.reset()
        
    # Must be called regularly
    def update(self):
        # Free preview display after a period
        if not self.__stay and self.label.override_text and self.__period and self.__period.exceeded:
            self.label.override_text = None
            self.label.update_label()

        # Blink
        if self.__blink and self.label.override_text and self.__blink_period and self.__blink_period.exceeded:
            self.__blink_state = not self.__blink_state

            if self.__blink_state:
                self.label.text_color = self.__blink_color
            else:
                self.label.text_color = self.__orig_color

