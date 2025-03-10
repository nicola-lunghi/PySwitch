from .callbacks import Callback
from .actions import Action

class PagerAction(Callback, Action):
    class _EnableCallback(Callback):
        def __init__(self, pager):
            super().__init__()
            self.__pager = pager

        def enabled(self, action):
            return (action.id == self.__pager.current_page_id)

    def __init__(self, 
                 pages,                         # This has to be a list of dicts like follows:
                                                # {
                                                #      "id": Page ID. All actions with this ID will be enabled
                                                #      "color": Page color. LEDs and label will be colored this way (for the brightness, there is a separate parameter)
                                                #      "text": Label text for the page
                                                # }
                 led_brightness = 0.15,         # LED brightness for the action (fixed) in range [0..1]
                 mappings = [],                 # List of mappings the paging depends on (optional)
                 use_leds = True,
                 id = None,
                 display = None,
                 enable_callback = None
        ):
        Callback.__init__(self, mappings)
        Action.__init__(self, {
            "useSwitchLeds": use_leds,
            "id": id,
            "display": display,
            "enableCallback": enable_callback
        })

        self.__pages = pages
        self.__led_brightness = led_brightness

        self.__current_page_index = -1
        self.current_page_id = None

        self.enable_callback = PagerAction._EnableCallback(self)

    # Must be called before usage
    def init(self, appl, switch):
        Action.init(self, appl, switch)

        self.__current_page_index = 0
        self.current_page_id = self.__pages[self.__current_page_index]["id"] if len(self.__pages) > 0 else None

    # Called when the switch is pushed down
    def push(self):
        if not len(self.__pages):
            return
        
        if self.__current_page_index < 0:
            return 
        
        # Next page
        self.__current_page_index += 1
        while self.__current_page_index >= len(self.__pages):
            self.__current_page_index = 0

        self.current_page_id = self.__pages[self.__current_page_index]["id"] if len(self.__pages) > 0 else None

        self.update_displays()

    def update_displays(self):
        if not len(self.__pages):
            return

        if self.__current_page_index < 0:
            return 
        
        if not self.enabled:
            return
        
        page = self.__pages[self.__current_page_index]
        
        if "color" in page:
            self.switch_color = page["color"]

        self.switch_brightness = self.__led_brightness

        if self.label:
            self.label.text = page["text"] if "text" in page else ""
            
            if "color" in page and self.label.back_color:
                self.label.back_color = page["color"]