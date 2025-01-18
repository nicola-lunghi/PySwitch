from ....controller.actions import PushButtonAction
from ....controller.callbacks import BinaryParameterCallback
from ....misc import Colors

# Binary parameters (for all binary parameter mappings which support 0/1 values for on/off)
def BINARY_SWITCH(mapping, 
                  display = None, 
                  text = "", 
                  mode = PushButtonAction.HOLD_MOMENTARY, 
                  color = Colors.WHITE, 
                  id = False, 
                  use_leds = True, 
                  enable_callback = None,
                  value_on = 1,
                  value_off = 0,
                  reference_value = None,
                  comparison_mode = BinaryParameterCallback.GREATER_EQUAL
    ):
    return PushButtonAction({
        "callback": BinaryParameterCallback(
            mapping = mapping,
            text = text,
            color = color,
            value_enable = value_on,
            value_disable = value_off,
            reference_value = reference_value,
            comparison_mode = comparison_mode
        ),
        "mode": mode,
        "display": display,
        "id": id,
        "useSwitchLeds": use_leds,
        "enableCallback": enable_callback
    })
