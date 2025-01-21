from .callbacks import Callback
from .actions import Action

class PagerAction(Callback, Action):
    class _EnableCallback(Callback):
        def __init__(self, pager):
            super().__init__()
            self.__pager = pager

        def enabled(self, action):
            return (action.id == self.__pager.current_page_id)

    # pages has to be a list of dicts like follows:
    # {
    #      "id": Page ID. All actions with this ID will be enabled
    #      "color": Page color. LEDs and label will be colored this way (for the brightness, there is a separate parameter)
    #      "text": Label text for the page
    # }
    def __init__(self, pages, led_brightness = 0.15, mappings = [], config = {}):
        # Enable LEDs only if a color is set
        if not "useSwitchLeds" in config:
            for page in pages:
                if "color" in page:
                    config["useSwitchLeds"] = True
                    break

        Callback.__init__(self, mappings)
        Action.__init__(self, config)

        self.__pages = pages
        self.__led_brightness = led_brightness

        self.__current_page_index = -1
        self.current_page_id = None

        self.enable_callback = PagerAction._EnableCallback(self)

    # Must be called before usage
    def init(self, appl, switch):
        Action.init(self, appl, switch)

        self.__current_page_index = 0
        self.current_page_id = self.__pages[self.__current_page_index]["id"]

    # Called when the switch is pushed down
    def push(self):
        if self.__current_page_index < 0:
            return 
        
        # Next page
        self.__current_page_index += 1
        while self.__current_page_index >= len(self.__pages):
            self.__current_page_index = 0

        self.current_page_id = self.__pages[self.__current_page_index]["id"]

        self.update_displays()

    def update_displays(self):
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