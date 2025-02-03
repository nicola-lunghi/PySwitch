from ....controller.actions import PushButtonAction
from ....controller.callbacks import BinaryParameterCallback
from ...kemper import NUM_RIGS_PER_BANK, BANK_COLORS, NUM_BANKS
from ....misc import Colors, get_option

from ..mappings.bank import MAPPING_NEXT_BANK, MAPPING_PREVIOUS_BANK
from .rig_select import RIG_SELECT_DISPLAY_CURRENT_RIG, RIG_SELECT_DISPLAY_TARGET_RIG

# Next bank (keeps rig index)
def BANK_UP(display = None, 
            id = False, 
            use_leds = True, 
            enable_callback = None,
            dim_factor = "off",                               # Can be "off", "on" or a value in range [0..1]
            led_brightness = "off",                           # Can be "off", "on" or a value in range [0..1]
            text = "Bank up",
            text_callback = None,                             # Optional callback for setting the text. Footprint: def callback(action, bank, rig) -> String where bank and rig are int starting from 0.
            color = None,                                     # Override color (if no color_callback is passed)
            color_callback = None,                            # Optional callback for setting the color. Footprint: def callback(action, bank, rig) -> (r, g, b) where bank and rig are int starting from 0.
            display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG     # Display mode (same as for RIG_SELECT, see definitions above)
    ):
    return PushButtonAction({
        "callback": KemperBankChangeCallback(
            mapping = MAPPING_NEXT_BANK(),
            offset = 1,
            dim_factor = dim_factor,
            display_mode = display_mode,
            led_brightness = led_brightness,
            color = color,
            color_callback = color_callback,
            text = text,
            text_callback = text_callback
        ),
        "mode": PushButtonAction.ONE_SHOT,
        "display": display,
        "id": id,
        "useSwitchLeds": use_leds,
        "enableCallback": enable_callback
    })

# Previous bank (keeps rig index)
def BANK_DOWN(display = None, 
                id = False, 
                use_leds = True, 
                enable_callback = None,
                dim_factor = "off",                               # Can be "off", "on" or a value in range [0..1]
                led_brightness = "off",                           # Can be "off", "on" or a value in range [0..1]
                text = "Bank dn", 
                text_callback = None,                             # Optional callback for setting the text. Footprint: def callback(action, bank, rig) -> String where bank and rig are int starting from 0.
                color = None,                                     # Override color (if no color_callback is passed)
                color_callback = None,                            # Optional callback for setting the color. Footprint: def callback(action, bank, rig) -> (r, g, b) where bank and rig are int starting from 0.
                display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG     # Display mode (same as for RIG_SELECT, see definitions above)
    ):
    return PushButtonAction({
        "callback": KemperBankChangeCallback(
            mapping = MAPPING_PREVIOUS_BANK(),
            offset = -1,
            dim_factor = dim_factor,
            display_mode = display_mode,
            led_brightness = led_brightness,
            color = color,
            color_callback = color_callback,
            text = text,
            text_callback = text_callback
        ),
        "mode": PushButtonAction.ONE_SHOT,
        "display": display,
        "id": id,
        "useSwitchLeds": use_leds,
        "enableCallback": enable_callback
    })


# Custom callback showing current bank color (only used by Bank up/down)
class KemperBankChangeCallback(BinaryParameterCallback):
    def __init__(self, 
                    mapping, 
                    offset,
                    dim_factor,
                    display_mode,
                    led_brightness,
                    color,
                    color_callback,
                    text,
                    text_callback
        ):            
        super().__init__(
            mapping = mapping,
            value_enable = 0,
            value_disable = 0,
            comparison_mode = self.NO_STATE_CHANGE
        )

        self.__mapping = mapping
        self.__dim_factor_p = dim_factor
        self.__led_brightness_p = led_brightness
        self.__display_mode = display_mode

        self.__color = color
        self.__color_callback = color_callback
        self.__offset = offset

        self.__text = text
        self.__text_callback = text_callback        

    def init(self, appl, listener = None):
        super().init(appl, listener)
        self.__appl = appl

        if self.__dim_factor_p == "off":
            self.__dim_factor = get_option(appl.config, "displayDimFactorOff", 0.2)
        elif self.__display_mode == "on":
            self.__dim_factor = get_option(appl.config, "displayDimFactorOn", 1)
        else:
            self.__dim_factor = self.__dim_factor_p

        if self.__led_brightness_p == "off":
            self.__led_brightness = get_option(appl.config, "ledBrightnessOff", 0.02)
        elif self.__led_brightness_p == "on":
            self.__led_brightness = get_option(appl.config, "ledBrightnessOn", 0.3)
        else:
            self.__led_brightness = self.__led_brightness_p

    def state_changed_by_user(self, action):
        super().state_changed_by_user(action)
        self.__appl.shared["morphStateOverride"] = 0

    def update_displays(self, action):
        if self.__mapping.value == None:
            # Fallback to default behaviour
            if action.label:
                action.label.text = self.__text
                action.label.back_color = self.dim_color(Colors.WHITE, self.__dim_factor)

            action.switch_color = Colors.WHITE
            action.switch_brightness = self.__led_brightness
            return
        
        # Calculate bank and rig numbers in range [0...]
        bank = int(self.__mapping.value / NUM_RIGS_PER_BANK)
        rig = self.__mapping.value % NUM_RIGS_PER_BANK
        
        if self.__color_callback:
            bank_color = self.__color_callback(action, bank, rig)
        elif self.__color:
            bank_color = self.__color
        else:
            bank_color = BANK_COLORS[bank % len(BANK_COLORS)] if self.__display_mode == RIG_SELECT_DISPLAY_CURRENT_RIG else BANK_COLORS[(len(BANK_COLORS) + bank + self.__offset) % len(BANK_COLORS)]

        # Label text
        if action.label:
            action.label.back_color = self.dim_color(bank_color, self.__dim_factor)

            if self.__text_callback:
                if self.__display_mode == RIG_SELECT_DISPLAY_CURRENT_RIG:
                    action.label.text = self.__text_callback(action, bank, rig)

                elif self.__display_mode == RIG_SELECT_DISPLAY_TARGET_RIG:
                    target_bank = bank + self.__offset
                    
                    while target_bank >= NUM_BANKS:
                        target_bank -= NUM_BANKS
                    
                    while target_bank < 0:
                        target_bank += NUM_BANKS

                    action.label.text = self.__text_callback(action, target_bank, rig)
                else:
                    raise Exception() #"Invalid display mode: " + repr(display_mode))
            else:
                action.label.text = self.__text

        action.switch_color = bank_color
        action.switch_brightness = self.__led_brightness