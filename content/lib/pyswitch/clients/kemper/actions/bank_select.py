from ...kemper import NUM_RIGS_PER_BANK, BANK_COLORS
from ....controller.actions import PushButtonAction
from ....controller.callbacks import BinaryParameterCallback
from ....misc import get_option, Colors, PeriodCounter

from ..mappings.select import MAPPING_BANK_AND_RIG_SELECT, MAPPING_BANK_SELECT
from .rig_select import RIG_SELECT_DISPLAY_CURRENT_RIG, RIG_SELECT_DISPLAY_TARGET_RIG

# Selects a specific bank, keeping the current rig, or toggles between two banks (if bank_off is also provided). 
# Banks are indexed starting from one, range: [1..126].    
def BANK_SELECT(bank, 
                bank_off = None,
                preselect = False,                              # If False, the bank is switched immediately (by sending a rig select command after bank preselect). If True, only the bank preselect is sent.
                display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG,  # Display mode (see definitions above)
                display = None, 
                id = False, 
                use_leds = True, 
                enable_callback = None,
                color_callback = None,                          # Optional callback for setting the color. Footprint: def callback(action, bank, rig) -> (r, g, b) where bank and rig are int starting from 0.
                color = None,                                   # Color override (if no color callback is passed)
                text_callback = None,                           # Optional callback for setting the text. Footprint: def callback(action, bank, rig) -> String where bank and rig are int starting from 0.
                text = None                                     # Text override (if no text callback is passed)
    ):
    
    return PushButtonAction({
        "display": display,
        "mode": PushButtonAction.LATCH,
        "id": id,
        "useSwitchLeds": use_leds,
        "callback": KemperBankSelectCallback(
            mapping = MAPPING_BANK_AND_RIG_SELECT(0),
            bank = bank,
            bank_off = bank_off,
            text = text,
            text_callback = text_callback,
            color = color,
            color_callback = color_callback,
            display_mode = display_mode,
            preselect = preselect
        ),
        "enableCallback": enable_callback
    })


# Callback implementation for Bank Select, showing bank colors and rig/bank info
class KemperBankSelectCallback(BinaryParameterCallback):
    def __init__(self,
                    mapping,
                    bank,
                    bank_off,
                    text, 
                    text_callback,
                    color,
                    color_callback,
                    display_mode,
                    preselect,
                    preselect_blink_interval = 400
        ):
        super().__init__(
            mapping = mapping
        )

        self.__mapping = mapping
        self.__bank = bank
        self.__bank_off = bank_off
        self.__text = text
        self.__text_callback = text_callback
        self.__color = color
        self.__color_callback = color_callback
        self.__display_mode = display_mode

        self.__current_value = -1
        self.__current_state = -1

        self.__preselect = preselect
        if preselect:
            self.__preselect_blink_period = PeriodCounter(preselect_blink_interval)
            self.__blink_state = False

        self.__action = None

    def init(self, appl, listener = None):
        super().init(appl, listener)

        self.__default_dim_factor_off = get_option(appl.config, "displayDimFactorOff", 0.2)
        self.__default_led_brightness_off = get_option(appl.config, "ledBrightnessOff", 0.02)
        self.__default_led_brightness_on = get_option(appl.config, "ledBrightnessOn", 0.3)
        self.__appl = appl

    def update(self):
        BinaryParameterCallback.update(self)

        if self.__preselect and "preselectedBank" in self.__appl.shared and self.__appl.shared["preselectedBank"] == self.__bank - 1 and self.__preselect_blink_period.exceeded:
            self.__blink_state = not self.__blink_state

            self.update_displays(self.__action)

    def state_changed_by_user(self, action):
        self.__action = action

        # Bank and rig select
        if self.__mapping.value == None:
            return
        
        curr_bank = int(self.__mapping.value / NUM_RIGS_PER_BANK)         

        if self.__preselect:
            if "preselectedBank" in self.__appl.shared:
                # The kemper only accepts one bank preselect. All following bank preselects will be ignored.
                # So, we also do not accept any preselects when there is already one.
                return 
            
            set_mapping = MAPPING_BANK_SELECT()

            value_bank = [self.__bank - 1]
            if self.__bank_off != None:
                value_bank_off = [self.__bank_off - 1]

                if action.state:
                    self.__appl.shared["preselectedBank"] = self.__bank - 1
                else:
                    self.__appl.shared["preselectedBank"] = self.__bank_off - 1
            else:
                if curr_bank != self.__bank - 1:
                    self.__appl.shared["preselectedBank"] = self.__bank - 1

            for input in self.__appl.inputs:
                if hasattr(input, "pixels"):
                    for a in input.actions:
                        a.update_displays()

        else:
            curr_rig = self.__mapping.value % NUM_RIGS_PER_BANK
            set_mapping = MAPPING_BANK_AND_RIG_SELECT(curr_rig)

            value_bank = [self.__bank - 1, 1, 0]
            if self.__bank_off:
                value_bank_off = [self.__bank_off - 1, 1, 0]

            if "preselectedBank" in self.__appl.shared:
                del self.__appl.shared["preselectedBank"]

            self.__appl.shared["morphStateOverride"] = 0

        if self.__bank_off != None:
            if action.state:
                if curr_bank != self.__bank - 1:
                    self.__appl.client.set(set_mapping, value_bank)
            else:
                if curr_bank != self.__bank_off - 1:
                    self.__appl.client.set(set_mapping, value_bank_off)
        else:
            if curr_bank != self.__bank - 1:
                self.__appl.client.set(set_mapping, value_bank)

        # # Request value
        # self.update()

    def update_displays(self, action):
        self.__action = action

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
            action.feedback_state(curr_bank == (self.__bank - 1))
                            
            self.__current_value = self.__mapping.value
            self.__current_state = action.state

            # if "preselectedBank" in self.__appl.shared:
            #     del self.__appl.shared["preselectedBank"]

        if "preselectedBank" in self.__appl.shared and self.__appl.shared["preselectedBank"] == self.__bank - 1:
            is_current = self.__blink_state
        else:
            is_current = (curr_bank == (self.__bank - 1))

        if self.__color != None:
            bank_color = self.__color
        elif self.__color_callback:
            bank_color = self.__color_callback(action, curr_bank, curr_rig)
        else:
            bank_color = self._get_bank_color(action, curr_bank, self.__bank, self.__bank_off, self.__display_mode)
                        
        # Label text
        if action.label:
            if self.__display_mode == RIG_SELECT_DISPLAY_CURRENT_RIG:
                action.label.text = self._get_text(action, curr_bank, curr_rig) 
                action.label.back_color = self.dim_color(bank_color, self.__default_dim_factor_off)

            elif self.__display_mode == RIG_SELECT_DISPLAY_TARGET_RIG:
                if "preselectedBank" in self.__appl.shared:
                    action.label.back_color = bank_color if is_current else self.dim_color(bank_color, self.__default_dim_factor_off) 
                else:
                    action.label.back_color = bank_color if action.state else self.dim_color(bank_color, self.__default_dim_factor_off) 

                if is_current and self.__bank_off != None:
                    action.label.text = self._get_text(action, self.__bank_off - 1, curr_rig)
                else:
                    action.label.text = self._get_text(action, self.__bank - 1, curr_rig)

            else:
                raise Exception()  #"Invalid display mode: " + repr(display_mode))

        # LEDs
        action.switch_color = bank_color

        if self.__display_mode == RIG_SELECT_DISPLAY_TARGET_RIG:
            if "preselectedBank" in self.__appl.shared:
                if is_current:
                    action.switch_brightness = self.__default_led_brightness_on
                else:
                    action.switch_brightness = self.__default_led_brightness_off
            else:
                if action.state:
                    action.switch_brightness = self.__default_led_brightness_on
                else:
                    action.switch_brightness = self.__default_led_brightness_off
        else:
            action.switch_brightness = self.__default_led_brightness_off

    # Get text for the label
    def _get_text(self, action, bank, rig):
        if self.__text:
            return self.__text
        elif self.__text_callback:
            return self.__text_callback(action, bank, rig)
        else:
            return "Bank " + repr(bank + 1)
            
    # Default color callback for bank color
    def _get_bank_color(self, action, curr_bank, bank, bank_off, display_mode):
        is_current = (curr_bank == (bank - 1))

        if display_mode == RIG_SELECT_DISPLAY_TARGET_RIG:
            if is_current and bank_off != None:
                return BANK_COLORS[(bank_off - 1) % len(BANK_COLORS)]
            else:
                return BANK_COLORS[(bank - 1) % len(BANK_COLORS)]

        elif display_mode == RIG_SELECT_DISPLAY_CURRENT_RIG:
            return BANK_COLORS[curr_bank % len(BANK_COLORS)]

        else:
            raise Exception() #"Invalid display mode: " + repr(display_mode))         