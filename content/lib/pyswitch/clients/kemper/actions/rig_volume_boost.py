from ....controller.actions import PushButtonAction
from ....controller.callbacks import BinaryParameterCallback
from ...kemper import NRPN_VALUE
from ....misc import Colors

from ..mappings.rig import MAPPING_RIG_VOLUME

# Volume boost function, based on setting rig volume to a certain boost value. To 
# make sense, all rig volumes have to be zero in your rigs! You can then set the
# boost rig volume by passing a value in range [0..1] (corresponding to the range of the
# rig volume paramneter: 0.5 is 0dB, 0.75 is +6dB, 1.0 is +12dB)
def RIG_VOLUME_BOOST(boost_volume,                              # Boost volume
                                                                # Comment test line 2
                                                                
                     display = None, 
                     mode = PushButtonAction.HOLD_MOMENTARY, 
                     color = Colors.PINK, 
                     id = False, 
                     use_leds = True, 
                     text = "RigBoost", 
                     remember_off_value = True, 
                     enable_callback = None
    ):
    return PushButtonAction({
        "callback": BinaryParameterCallback(
            mapping = MAPPING_RIG_VOLUME(),
            text = text,
            color = color,
            value_enable = NRPN_VALUE(boost_volume),
            value_disable = NRPN_VALUE(0.5) if not remember_off_value else "auto",    # 0.5 = 0dB
        ),
        "mode": mode,
        "display": display,
        "id": id,
        "useSwitchLeds": use_leds,
        "enableCallback": enable_callback
    })