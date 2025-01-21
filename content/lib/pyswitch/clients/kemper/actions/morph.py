from ....controller.actions import PushButtonAction
from ....controller.callbacks import BinaryParameterCallback
from ....misc import Colors

from ..mappings.morph import MAPPING_MORPH_BUTTON, MAPPING_MORPH_PEDAL

# Morph button (faded change of morph state) with fixed color.
def MORPH_BUTTON(display = None, 
                 text = "Morph", 
                 id = False, 
                 use_leds = True, 
                 enable_callback = None, 
                 color = "kemper"         # Can be "kemper" or a fixed color
    ):
    if color == "kemper":
        cb = KemperMorphCallback(
            mapping = MAPPING_MORPH_BUTTON(),
            text = text,
            comparison_mode = BinaryParameterCallback.NO_STATE_CHANGE,
            led_brightness_off = "on",
            display_dim_factor_off = "on",
        )
    else:        
        cb = BinaryParameterCallback(
            mapping = MAPPING_MORPH_BUTTON(),
            text = text,
            color = color,
            comparison_mode = BinaryParameterCallback.NO_STATE_CHANGE,
            led_brightness_off = "on",
            display_dim_factor_off = "on",
        )
    
    return PushButtonAction({
        "callback": cb,
        "mode": PushButtonAction.MOMENTARY,
        "useSwitchLeds": use_leds,
        "display": display,
        "id": id,
        "enableCallback": enable_callback
    })

# Morph display only
def MORPH_DISPLAY(display = None, text = "Morph", id = False, use_leds = True, enable_callback = None):
    return PushButtonAction({
        "callback": KemperMorphCallback(
            mapping = MAPPING_MORPH_PEDAL(),
            text = text,
            comparison_mode = BinaryParameterCallback.NO_STATE_CHANGE,
            led_brightness_off = "on",
            display_dim_factor_off = "on",
            suppress_send = True
        ),
        "useSwitchLeds": use_leds,
        "display": display,
        "id": id,
        "enableCallback": enable_callback
    })


# BinaryParameterCallback for morph pedal mapping, with colors reflecting the morph state
class KemperMorphCallback(BinaryParameterCallback):

    COLOR_BASE = Colors.RED
    COLOR_MORPH = Colors.BLUE

    def __init__(self, 
                 mapping,
                 text = "Morph", 
                 value_enable = 1, 
                 value_disable = 0, 
                 reference_value = None, 
                 comparison_mode = BinaryParameterCallback.GREATER_EQUAL, 
                 display_dim_factor_on = None,
                 display_dim_factor_off = None,
                 led_brightness_on = None,
                 led_brightness_off = None,
                 suppress_send = False
        ):

        def get_color(action, value):
            if value == None:
                return Colors.WHITE
            
            r_diff = self.COLOR_MORPH[0] - self.COLOR_BASE[0]
            g_diff = self.COLOR_MORPH[1] - self.COLOR_BASE[1]
            b_diff = self.COLOR_MORPH[2] - self.COLOR_BASE[2]

            v = value / 16383

            return (
                self.COLOR_BASE[0] + int(r_diff * v),
                self.COLOR_BASE[1] + int(g_diff * v),
                self.COLOR_BASE[2] + int(b_diff * v),
            )
        
        super().__init__(
            mapping = mapping, 
            color_callback = get_color,
            text = text, 
            value_enable = value_enable, 
            value_disable = value_disable, 
            reference_value = reference_value, 
            comparison_mode = comparison_mode, 
            display_dim_factor_on = display_dim_factor_on, 
            display_dim_factor_off = display_dim_factor_off, 
            led_brightness_on = led_brightness_on, 
            led_brightness_off = led_brightness_off
        )

        self.__suppress_send = suppress_send

    def state_changed_by_user(self, action):
        if self.__suppress_send:
            return
        
        super().state_changed_by_user(action)