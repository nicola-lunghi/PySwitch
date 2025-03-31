from ...misc import Updateable, PeriodCounter
from adafruit_midi.system_exclusive import SystemExclusive

class EncoderAction(Updateable):

    # Use this action for all rotary encoders like wheels. The push-down switch of the encoder is 
    # not addressed here: This is represented as a separate switch, and can be linked to the same actions as a normal foot switch.
    def __init__(self, 
                 mapping,                           # Parameter mapping to be controlled
                 max_value = None,                  # Maximum value of the mapping (set to None for auto-detect: 16383 for NRPN, 127 for CC)
                 step_width = None,                 # Increment/Decrement for one encoder step. Set to None for auto-detect (NRPN: 80, CC: 1)
                 enable_callback = None,            # Callback to set enabled state (optional). Must contain an enabled(action) function.
                 id = None,
                 accept_action = None,              # Action to acknowledge the entered value. If None, the encoder directly sets values as you turn it. 
                                                    # If you pass an Encoder Button action, the value will just be displayed and the MIDI command to set 
                                                    # it will be sent when the Button action is triggered.
                                                    # 
                                                    # If you use this, you will also need a preview display label (see below)
                 cancel_action = None,              # Action to cancel a preselection (only makes sense with accept_action set). Must also be of type Encoder Button.
                 preview_display = None,            # If assigned, the adjusted value will be displayed in the passed DisplayLabel when the encoder is adjusted. 
                                                    # 
                                                    # This just makes sense in conjunction with an accept action (see above).
                 preview_timeout_millis = 1500,     # This is the amount of time (milliseconds) after which the 
                                                    # preview display will return to its normal state.
                 preview_blink_period_millis = 400, # Blink period for preview (if an accept action is set)
                 preview_blink_color = (200, 200, 200), # Alternative color to be used when blinking.
                 preview_reset_mapping = None,      # A parameter mapping (optional) which will be tracked. If the value changes, the preselect mode will be reset.
                 convert_value = None,              # Optional conversion routine for displaying values: (value) => string
        ):
        if isinstance(mapping.set, SystemExclusive):
            if max_value == None:
                max_value = 16383
            if step_width == None:
                step_width = 80
        else:
            if max_value == None:
                max_value = 127
            if step_width == None:
                step_width = 1

        self.id = id
        self.__mapping = mapping
        self.__max_value = max_value
        self.__step_width = step_width

        self.__enable_callback = enable_callback
        if self.__enable_callback:
            self.__enable_callback.action = self

        self.__last_pos = -1
        self.__last_value = -1
        self.__convert_value = convert_value

        if accept_action:
            accept_action.callback.register_encoder(self, False)

        if cancel_action:
            cancel_action.callback.register_encoder(self, True)
            
        self.__preselect = (accept_action != None)
        self.__preselect_active = False

        self.__preview_display = preview_display        
        if preview_display:
            self.__preview_period = PeriodCounter(preview_timeout_millis)
                
            if accept_action:
                self.__preview_blink_period = PeriodCounter(preview_blink_period_millis)
                self.__preview_blink_state = False
                self.__preview_orig_color = preview_display.text_color
                self.__preview_blink_color = preview_blink_color

                self.__preview_reset_mapping = preview_reset_mapping
                self.__preview_reset_last_value = None
                
    @property
    def enabled(self):
        return self.__enable_callback.enabled(self) if self.__enable_callback else True

    def init(self, appl):
        self.__appl = appl

        appl.client.register(self.__mapping)

        if self.__preview_display and self.__preselect and self.__preview_reset_mapping:
            appl.client.register(self.__preview_reset_mapping)

    def update(self):
        self.__appl.client.request(self.__mapping)

        if self.__preview_display:
            if self.__preselect_active and self.__preselect and self.__preview_blink_period.exceeded:
                # Blink when preview is active
                self.__preview_blink_state = not self.__preview_blink_state

                if self.__preview_blink_state:
                    self.__preview_display.text_color = self.__preview_blink_color
                else:
                    self.__preview_display.text_color = self.__preview_orig_color

    # Process the current encoder position
    def process(self, position):
        if self.__last_pos == -1:
            self.__last_pos = position

        if self.__preview_display and self.__preselect and self.__preview_reset_mapping:
            if self.__preview_reset_mapping.value != self.__preview_reset_last_value:
                if self.__preview_reset_mapping.value != None and self.__preview_reset_last_value != None:
                    self.cancel()

                self.__preview_reset_last_value = self.__preview_reset_mapping.value

        if self.__last_pos == position:
            if self.__preview_display:
                if not self.__preselect_active and self.__preview_display.override_text and self.__preview_period.exceeded:
                    # Free preview display after a period
                    self.__preview_display.override_text = None
                    self.__preview_display.update_label()
                
            return
                        
        if self.__mapping.value == None:
            self.__mapping.value = 0
            
        add_value = (position - self.__last_pos) * self.__step_width        
        self.__last_pos = position

        if not self.__preselect:
            v = self.__mapping.value + add_value
        else:
            v = self.__last_value + add_value

        if v < 0:
            v = 0
        if v > self.__max_value:
            v = self.__max_value

        if self.__last_value != v:
            self.__last_value = v
            
            if not self.__preselect:
                self.accept()
            else:
                self.__preselect_active = True

            if self.__preview_display:
                if not self.__convert_value:
                    prefix = f"{ self.__mapping.name }: " if self.__mapping.name else ""
                    val = round(v * 100 / self.__max_value)

                    self.__preview_display.override_text = f"{ prefix }{ str(val) }%"
                else:
                    self.__preview_display.override_text = self.__convert_value(v)
                
                self.__preview_display.update_label()

    # Send the last value and reset preview display
    def accept(self):
        if self.__last_value == -1:
            return
        
        if self.__preselect and not self.__preselect_active:
            return
        
        # Send message
        self.__appl.client.set(self.__mapping, self.__last_value)
        self.__mapping.value = self.__last_value

        self.cancel()

        if self.__preview_display:
            self.__preview_period.reset()

    # Cancel preselection
    def cancel(self):
        self.__preselect_active = False

        self.__last_value = self.__mapping.value

        if self.__preview_display and self.__preselect:
            self.__preview_display.text_color = self.__preview_orig_color