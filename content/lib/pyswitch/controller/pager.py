from .callbacks import Callback
from .actions import Action

class PagerAction(Callback, Action):
    class _EnableCallback(Callback):
        def __init__(self, pager):
            super().__init__()
            self.__pager = pager

        def enabled(self, action):
            return (action.id == self.__pager.current_page_id)

    # Proxy action which directly selects a page
    class _DirectPageProxy(Action):
        def __init__(self, pager, page_index, use_leds, id, display, enable_callback):
            Action.__init__(self, {
                "useSwitchLeds": use_leds,
                "id": id,
                "display": display,
                "enableCallback": enable_callback
            })
            self.__pager = pager
            self.__page_index = page_index

        # Called when the switch is pushed down
        def push(self):
            if not self.__pager.pages: 
                return
            
            if self.__page_index == None:
                return
            
            self.__pager.current_page_index = self.__page_index
            self.__pager.current_page_id = self.__pager.pages[self.__pager.current_page_index]["id"] if len(self.__pager.pages) > 0 else None
        
            self.__pager.update_displays()

        def update_displays(self):
            if self.__page_index == None:
                return
            
            if len(self.__pager.pages) <= self.__page_index - 1:
                return

            if not self.enabled:
                return
            
            page = self.__pager.pages[self.__page_index]
            self.__pager.apply_page_to_action_displays(self, page, self.__page_index)


    # The PagerAction is used to control multiple other actions to provide paging for specifiec actions.
    # Define this action for one switch, and select it in the actions to control by setting the enable_callback parameter and page ID for those actions.
    # 
    # If you want to rotate through pages, just use this action with select_page set to None. 
    # 
    # If you want to have one switch dedicated to select every page, set select_page to the page you want to select with this switch, and use the Pager Proxy action for the other switches.
    def __init__(self, 
                 pages,                         # This has to be a list of dicts like follows:
                                                # {
                                                #      "id": Page ID. All actions with this ID will be enabled
                                                #      "color": Page color. LEDs and label will be colored this way (for the brightness, there is a separate parameter)
                                                #      "text": Label text for the page
                                                # }

                 select_page = None,            # If none, the pages will be rotated. If set to a page ID, the action will select the passed page (use a 
                                                # proxy() for directly selecting other pages)

                 led_brightness = 0.15,         # LED brightness for the pager in range [0..1]. Only used when selet_page is None (rotate mode).
                 led_brightness_off = 0.02,     # LED brightness for the pager when select_page is set and the page is not currently selected. Range [0..1].
                 led_brightness_on = 0.3,       # LED brightness for the pager when select_page is set and the page is currently selected. Range [0..1].
                 display_dim_factor_on = 1,     # Display dim factor used when in rotation mode or if the current page is select_page
                 display_dim_factor_off = 0.2,  # Display dim factor used when select_page is selt and the current page is not select_page
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

        self.pages = pages
        self.led_brightness = led_brightness
        self.led_brightness_on = led_brightness_on
        self.led_brightness_off = led_brightness_off
        self.display_dim_factor_on = display_dim_factor_on
        self.display_dim_factor_off = display_dim_factor_off
        self.__proxies = []

        self.current_page_index = -1
        self.current_page_id = None
        self.__select_page_index = self._get_page_index(select_page) if select_page else None

        self.enable_callback = PagerAction._EnableCallback(self)

    # This controls a PagerAction from another switch, making it possible to directly select pages with dedicated switches.
    #
    # You always need to have one PagerAction which defines the pages and selects one of them (see the select_page parameter of PagerAction). For selecting the other pages, create Pager Proxy actions on the other switches.
    def proxy(self, page_id, use_leds = True, id = None, display = None, enable_callback = None):
        proxy = self._DirectPageProxy(self, 
                                      page_index = self._get_page_index(page_id),
                                      use_leds = use_leds,
                                      id = id,
                                      display = display,
                                      enable_callback = enable_callback)
        
        self.__proxies.append(proxy)
        return proxy

    # Determines the page index for a given page ID
    def _get_page_index(self, page_id):
        for index in range(len(self.pages)):
            if self.pages[index]["id"] == page_id:
                return index
        return None

    # Must be called before usage
    def init(self, appl, switch):
        Action.init(self, appl, switch)

        self.current_page_index = 0
        self.current_page_id = self.pages[self.current_page_index]["id"] if len(self.pages) > 0 else None

    # Called when the switch is pushed down
    def push(self):
        if not len(self.pages):
            return
        
        if self.current_page_index < 0:
            return 
        
        if self.__select_page_index != None:
            # Direct select
            self.current_page_index = self.__select_page_index
        else:
            # Next page
            self.current_page_index += 1
            while self.current_page_index >= len(self.pages):
                self.current_page_index = 0

        self.current_page_id = self.pages[self.current_page_index]["id"] if len(self.pages) > 0 else None

        self.update_displays()

    def update_displays(self):
        if not len(self.pages):
            return

        if self.current_page_index < 0:
            return 
        
        if not self.enabled:
            return
        
        page = self.pages[self.current_page_index if self.__select_page_index == None else self.__select_page_index]
        self.apply_page_to_action_displays(self, page, self.__select_page_index)

        for proxy in self.__proxies:
            proxy.update_displays()

    # Used by this class and proxies
    def apply_page_to_action_displays(self, action, page, page_index):
        if not hasattr(action, "switch"):
            return
        
        page_color = page["color"] if "color" in page else None

        if page_color:
            action.switch_color = page["color"]

        if action.label:
            action.label.text = page["text"] if "text" in page else ""
            
        if page_index == None:
            action.switch_brightness = self.led_brightness

            if action.label and action.label.back_color and page_color:
                action.label.back_color = page_color
        else:
            is_current = page_index == self.current_page_index

            action.switch_brightness = self.led_brightness_on if is_current else self.led_brightness_off     

            if action.label and action.label.back_color and page_color:
                factor = self.display_dim_factor_on if is_current else self.display_dim_factor_off
                action.label.back_color = (
                    int(page_color[0] * factor),
                    int(page_color[1] * factor),
                    int(page_color[2] * factor)
                )
