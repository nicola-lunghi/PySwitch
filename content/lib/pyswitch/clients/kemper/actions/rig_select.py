from ...kemper import RIG_SELECT_DISPLAY_CURRENT_RIG, RIG_SELECT_DISPLAY_TARGET_RIG, NUM_RIGS_PER_BANK, BANK_COLORS, KemperMappings
from ....controller.actions import PushButtonAction
from ....controller.callbacks import BinaryParameterCallback
from ....misc import get_option, Colors

# Selects a specific rig, or toggles between two rigs (if rig_off is also provided) in
# the current bank. Rigs are indexed starting from one, range: [1..5].
def RIG_SELECT(rig, 
               rig_off = None,                                 # If set, this defines the "off" rig chosen when the action is disabled. Set to "auto" to always remember the current rig as "off" rig
               bank = None,                                    # If set, a specific bank is selected. If None, the current bank is kept
               bank_off = None,                                # If set, this defines the "off" bank to be chosen when the action is disabled. Set to "auto" to always remember the current bank as "off" bank
               display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG,  # Display mode (see definitions above)
               display = None, 
               id = False, 
               use_leds = True, 
               enable_callback = None,
               color_callback = None,                          # Optional callback for setting the color. Footprint: def callback(action, bank, rig) -> (r, g, b) where bank and rig are int starting from 0.
               color = None,                                   # Color override (if no text callback is passed)
               text_callback = None,                           # Optional callback for setting the text. Footprint: def callback(action, bank, rig) -> String where bank and rig are int starting from 0.
               text = None,                                    # Text override (if no text callback is passed)
               auto_exclude_rigs = None                        # If rig_off is "auto", this can be filled with a tuple or list of rigs to exclude from "remembering" when disabled
    ):
    
    # Finally we can create the action definition ;)
    return PushButtonAction({
        "display": display,
        "mode": PushButtonAction.LATCH,
        "id": id,
        "useSwitchLeds": use_leds,
        "callback": _RigSelectCallback(
            rig = rig,
            rig_off = rig_off,
            bank = bank,
            bank_off = bank_off,
            color = color,
            color_callback = color_callback,
            display_mode = display_mode,
            text = text,
            text_callback = text_callback,
            auto_exclude_rigs = auto_exclude_rigs
        ),
        "enableCallback": enable_callback
    })  

# Callback implementation for Rig Select, showing bank colors and rig/bank info
class _RigSelectCallback(BinaryParameterCallback):
    def __init__(self,
                    rig,
                    rig_off,                     
                    bank,
                    bank_off,
                    color,
                    color_callback,
                    display_mode,
                    text,
                    text_callback,
                    auto_exclude_rigs = None
        ):
        
        if rig_off != None and bank != None and bank_off == None:
            raise Exception() #"Also provide bank_off")        

        if bank == None:
            mapping = KemperMappings.RIG_SELECT(rig - 1)
            mapping_disable = None if (rig_off == None or rig_off == "auto") else KemperMappings.RIG_SELECT(rig_off - 1)
            value_enable = [1, 0]
            value_disable = [1, 0]
        else:
            mapping = KemperMappings.BANK_AND_RIG_SELECT(rig - 1)
            mapping_disable = None if (rig_off == None or rig_off == "auto") else KemperMappings.BANK_AND_RIG_SELECT(rig_off - 1)
            value_enable = [bank - 1, 1, 0]
            value_disable = [bank - 1, 1, 0] if (bank_off == None or bank_off == "auto") else [bank_off - 1, 1, 0]

        super().__init__(
            mapping = mapping,
            mapping_disable = mapping_disable,
            value_enable = value_enable,
            value_disable = value_disable,
            reference_value = (bank - 1) * NUM_RIGS_PER_BANK + (rig - 1) if bank != None else None,
            comparison_mode = self.EQUAL if bank != None else BinaryParameterCallback.GREATER_EQUAL 
        )

        self.__current_value = -1
        self.__current_state = -1
        self.__mapping = mapping
        self.__bank = bank
        self.__bank_off = bank_off if bank_off != "auto" else 1
        self.__rig = rig
        self.__rig_off = rig_off if rig_off != "auto" else 1

        self.__rig_off_auto = True if rig_off == "auto" else False
        self.__bank_off_auto = (bank != None) if bank_off == "auto" else False

        self.__color_callback = color_callback
        self.__color = color

        self.__text_callback = text_callback
        self.__text = text

        self.__display_mode = display_mode

        self.__auto_exclude_rigs = auto_exclude_rigs

    def init(self, appl, listener = None):
        super().init(appl, listener)

        self.__default_dim_factor_off = get_option(appl.config, "displayDimFactorOff", 0.2)
        self.__default_led_brightness_off = get_option(appl.config, "ledBrightnessOff", 0.02)
        self.__default_led_brightness_on = get_option(appl.config, "ledBrightnessOn", 0.3)

        self.__appl = appl

    def state_changed_by_user(self, action):
        if "preselectedBank" in self.__appl.shared:
            set_mapping = self.__mapping
            value = self._value_enable
        else:
            if action.state:
                set_mapping = self.__mapping
                value = self._value_enable
            else:
                if self.mapping_disable:
                    set_mapping = self.mapping_disable
                else:
                    set_mapping = self.__mapping

                value = self._value_disable

        self.__appl.client.set(set_mapping, value)

        # # Request value
        # self.update()

    def update_displays(self, action):
        if self.__mapping.value == None:
            if action.label:
                action.label.text = ""
                action.label.back_color = self.dim_color(Colors.WHITE, self.__default_dim_factor_off)

            action.switch_color = Colors.WHITE
            action.switch_brightness = self.__default_led_brightness_off
            return
        
        # Calculate bank and rig numbers in range [0...]
        curr_bank = int(self.__mapping.value / NUM_RIGS_PER_BANK)
        curr_rig = self.__mapping.value % NUM_RIGS_PER_BANK
        
        if self.__mapping.value != self.__current_value or action.state != self.__current_state:
            if self.__bank != None:
                self.evaluate_value(action, self.__mapping.value)
            else:
                if self.__mapping.value != None:                        
                    action.feedback_state(curr_rig == self.__rig - 1) 
                else:
                    action.feedback_state(False)            

            self.__current_value = self.__mapping.value
            self.__current_state = action.state

            # Auto rig off: If we are not on the "on" rig, set the current rig as "off" rig
            if (not self.__auto_exclude_rigs or (curr_rig + 1) not in self.__auto_exclude_rigs) and self.__rig_off_auto and curr_rig != self.__rig - 1:
                if self.__bank != None:
                    self.mapping_disable = KemperMappings.BANK_AND_RIG_SELECT(curr_rig)
                else:
                    self.mapping_disable = KemperMappings.RIG_SELECT(curr_rig)

            if self.__bank_off_auto and curr_bank != self.__bank - 1:
                self.__bank_off = curr_bank + 1                    
                self._value_disable[0] = curr_bank

            if "preselectedBank" in self.__appl.shared:
                del self.__appl.shared["preselectedBank"]
            
        if self.__bank != None:
            is_current = (curr_rig == (self.__rig - 1) and curr_bank == (self.__bank - 1))
        else:
            if "preselectedBank" in self.__appl.shared:
                is_current = False
            else:
                is_current = (curr_rig == self.__rig - 1)
            
        bank_color = self._get_color(action, curr_bank, curr_rig, is_current)                    

        # Label text
        if action.label:
            if self.__display_mode == RIG_SELECT_DISPLAY_CURRENT_RIG:
                action.label.text = self._get_text(action, curr_bank, curr_rig) 
                action.label.back_color = self.dim_color(bank_color, self.__default_dim_factor_off)

            elif self.__display_mode == RIG_SELECT_DISPLAY_TARGET_RIG:
                if "preselectedBank" in self.__appl.shared:
                    action.label.back_color = self.dim_color(bank_color, self.__default_dim_factor_off) 
                    action.label.text = self._get_text(action, self.__appl.shared["preselectedBank"], self.__rig - 1)
                else:
                    action.label.back_color = bank_color if action.state else self.dim_color(bank_color, self.__default_dim_factor_off) 

                    if self.__bank != None:
                        if is_current and self.__rig_off != None and self.__bank_off != None:
                            action.label.text = self._get_text(action, self.__bank_off - 1, self.__rig_off - 1)
                        else:
                            action.label.text = self._get_text(action, self.__bank - 1, self.__rig - 1)
                    else:
                        if is_current and self.__rig_off != None:                    
                            action.label.text = self._get_text(action, curr_bank, self.__rig_off - 1) 
                        else:
                            action.label.text = self._get_text(action, curr_bank, self.__rig - 1)

            else:
                raise Exception()  #"Invalid display mode: " + repr(display_mode))

        # LEDs
        action.switch_color = bank_color

        if self.__display_mode == RIG_SELECT_DISPLAY_TARGET_RIG and action.state and not "preselectedBank" in self.__appl.shared:
            action.switch_brightness = self.__default_led_brightness_on
        else:
            action.switch_brightness = self.__default_led_brightness_off

    def _get_color(self, action, curr_bank, curr_rig, is_current):
        if self.__color:
            return self.__color
        
        if self.__color_callback:
            return self.__color_callback(action, curr_bank, curr_rig)

        if self.__display_mode == RIG_SELECT_DISPLAY_TARGET_RIG and "preselectedBank" in self.__appl.shared:
            return BANK_COLORS[self.__appl.shared["preselectedBank"] % len(BANK_COLORS)]

        if self.__bank == None:
            return BANK_COLORS[curr_bank % len(BANK_COLORS)]

        # is_current = (curr_rig == (self.__rig - 1) and curr_bank == (self.__bank - 1))

        if self.__display_mode == RIG_SELECT_DISPLAY_TARGET_RIG:
            if self.__bank_off != None and is_current:
                return BANK_COLORS[(self.__bank_off - 1) % len(BANK_COLORS)]
            else:
                return BANK_COLORS[(self.__bank - 1) % len(BANK_COLORS)]

        elif self.__display_mode == RIG_SELECT_DISPLAY_CURRENT_RIG:
            return BANK_COLORS[curr_bank % len(BANK_COLORS)]

        else:
            raise Exception() #"Invalid display mode: " + repr(display_mode))
        
    def _get_text(self, action, bank, rig):
        if self.__text_callback:
            return self.__text_callback(action, bank, rig)
        
        if self.__text:
            return self.__text
            
        return "Rig " + repr(bank + 1) + "-" + repr(rig + 1)
    