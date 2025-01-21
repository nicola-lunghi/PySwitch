from ....controller.actions import PushButtonAction
from ....controller.callbacks import BinaryParameterCallback, Callback

from .morph import KemperMorphCallback
from .rig_select import RIG_SELECT, RIG_SELECT_DISPLAY_TARGET_RIG

from ..mappings.morph import MAPPING_MORPH_PEDAL
from ..mappings.select import MAPPING_RIG_SELECT


# Adds morph state display on one LED to the rig select action. Returns a list of actions!
# For details on the parameters, see RIG_SELECT.
def RIG_SELECT_AND_MORPH_STATE(rig, 
                               rig_off = None, 
                               bank = None,
                               bank_off = None,
                               display = None, 
                               id = False, 
                               use_leds = True, 
                               enable_callback = None,
                               color_callback = None,
                               color = None,
                               text_callback = None,
                               text = None,
                               display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                               morph_display = None,                           # Optional DisplayLabel to show morph color
                               morph_use_leds = True,                          # Use the LEDs to show morph state?
                               morph_id = None,                                # Separate ID for the morph action. Default is the same id as specified with the "id" parameter.
                               morph_only_when_enabled = True,                 # Only show the morph state when the "on" rig is selected

):
    rig_select = RIG_SELECT(
        rig = rig,
        rig_off = rig_off,
        bank = bank,
        bank_off = bank_off,
        display_mode = display_mode,
        display = display,
        id = id,
        use_leds = use_leds,
        enable_callback = enable_callback,
        color_callback = color_callback,
        color = color,
        text_callback = text_callback,
        text = text
    )        
    
    return [
        # Rig select action
        rig_select,

        # Use a separate action to show morph state
        PushButtonAction({
            "callback": KemperMorphCallback(
                mapping = MAPPING_MORPH_PEDAL(),
                comparison_mode = BinaryParameterCallback.NO_STATE_CHANGE,
                led_brightness_off = "on",
                display_dim_factor_off = "on",
                suppress_send = True
            ),
            "useSwitchLeds": morph_use_leds,
            "display": morph_display,
            "id": morph_id if morph_id != None else id,
            "enableCallback": KemperMorphDisplayEnableCallback(
                action_rig_select = rig_select, 
                rig = rig, 
                morph_only_when_enabled = morph_only_when_enabled
            )
        })            
    ]


# Callback to enable the morph state display only when the rig is selected
class KemperMorphDisplayEnableCallback(Callback):
    def __init__(self, 
                    action_rig_select, 
                    rig, 
                    morph_only_when_enabled
        ):
        Callback.__init__(self)
        
        self.__action_rig_select = action_rig_select
        self.__morph_only_when_enabled = morph_only_when_enabled

        self.__mapping = MAPPING_RIG_SELECT(rig - 1)
        self.register_mapping(self.__mapping)

    def enabled(self, action):
        if self.__morph_only_when_enabled:
            return self.__action_rig_select.state and self.__action_rig_select.enabled
        else:
            return self.__action_rig_select.enabled
