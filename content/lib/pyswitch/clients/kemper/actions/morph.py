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
        # cb = BinaryParameterCallback(
        #     mapping = MAPPING_MORPH_BUTTON(),
        #     text = text,
        #     color = color,
        #     comparison_mode = BinaryParameterCallback.NO_STATE_CHANGE,
        #     led_brightness_off = "on",
        #     display_dim_factor_off = "on",
        # )
    
    return PushButtonAction({
        "callback": KemperMorphCallback(
            mapping = MAPPING_MORPH_BUTTON(),
            text = text,
            comparison_mode = BinaryParameterCallback.NO_STATE_CHANGE,
            led_brightness_off = "on",
            display_dim_factor_off = "on",
            color = color
        ),
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


###################################################################################################

def _get_color(action, value):
    if KemperMorphCallback.morph_value_override != None:
        value = KemperMorphCallback.morph_value_override
        
    if value == None:
        return Colors.WHITE

    cb = action.callback
    if cb.fix_color:
        return cb.fix_color

    v = value / 16383
    
    return (
        cb.COLOR_BASE[0] + int(cb.R_DIFF * v),
        cb.COLOR_BASE[1] + int(cb.G_DIFF * v),
        cb.COLOR_BASE[2] + int(cb.B_DIFF * v),
    )  

# BinaryParameterCallback for morph pedal mapping, with colors reflecting the morph state
class KemperMorphCallback(BinaryParameterCallback):

    COLOR_BASE = Colors.RED
    COLOR_MORPH = Colors.BLUE

    # Used by set_internal_state to globally override the color
    morph_value_override = None
    
    def __init__(self, 
                 mapping,
                 set_internal_state = True,    # If this is set, a global, internal morph state is used instead of the values coming from the Kemper.
                 color = "kemper",             # Can be "kemper" or a fixed color
                 text = "Morph", 
                 value_enable = 1, 
                 value_disable = 0, 
                 reference_value = 8191, 
                 comparison_mode = BinaryParameterCallback.GREATER_EQUAL, 
                 display_dim_factor_on = None,
                 display_dim_factor_off = None,
                 led_brightness_on = None,
                 led_brightness_off = None,
                 suppress_send = False
        ):

        KemperMorphCallback.R_DIFF = KemperMorphCallback.COLOR_MORPH[0] - KemperMorphCallback.COLOR_BASE[0]
        KemperMorphCallback.G_DIFF = KemperMorphCallback.COLOR_MORPH[1] - KemperMorphCallback.COLOR_BASE[1]
        KemperMorphCallback.B_DIFF = KemperMorphCallback.COLOR_MORPH[2] - KemperMorphCallback.COLOR_BASE[2]
        
        super().__init__(
            mapping = mapping, 
            color_callback = _get_color,
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

        self.__set_internal_state = set_internal_state
        self.__suppress_send = suppress_send
        self.fix_color = color if color != "kemper" else None

        if set_internal_state:
            KemperMorphCallback.morph_value_override = 0            


    def state_changed_by_user(self, action):
        if self.__suppress_send:
            return
        
        super().state_changed_by_user(action)

        if self.__set_internal_state and action.state:
            KemperMorphCallback.morph_value_override = 0 if (KemperMorphCallback.morph_value_override > 0) else 16383

    
    def evaluate_value(self, action, value):
        if self.__set_internal_state and value != None:
            # Morph value has changed from the outside
            KemperMorphCallback.morph_value_override = value

        super().evaluate_value(action, value)