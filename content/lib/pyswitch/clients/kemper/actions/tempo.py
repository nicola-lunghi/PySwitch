from ....controller.actions import PushButtonAction
from ....controller.callbacks import BinaryParameterCallback, Callback
from ....clients.kemper import KemperMappings
from ....misc import Colors

from ..mappings.tempo import MAPPING_TAP_TEMPO, MAPPING_TEMPO_DISPLAY

# Tap tempo
def TAP_TEMPO(display = None, color = Colors.DARK_GREEN, id = False, use_leds = False, enable_callback = None):
    return PushButtonAction({
        "callback": BinaryParameterCallback(
            mapping = MAPPING_TAP_TEMPO(),
            text = "Tap",
            color = color
        ),
        "mode": PushButtonAction.MOMENTARY,
        "display": display,
        "id": id,
        "useSwitchLeds": use_leds,
        "enableCallback": enable_callback
    })

# Show tempo (blinks on every beat)
def SHOW_TEMPO(display = None, color = Colors.LIGHT_GREEN, text = "Tempo", id = False, use_leds = True, enable_callback = None, led_brightness_on = 0.02, led_brightness_off = 0):
    return PushButtonAction({
        "callback": BinaryParameterCallback(
            mapping = MAPPING_TEMPO_DISPLAY(),
            text = text,
            color = color,
            led_brightness_on = led_brightness_on,
            led_brightness_off = led_brightness_off
        ),
        "display": display,
        "id": id,
        "useSwitchLeds": use_leds,
        "enableCallback": _ShowTempoEnableCallback(enable_callback)
    })


class _ShowTempoEnableCallback(Callback):
    def __init__(self, enable_callback):
        super().__init__()
        self.__enable_callback = enable_callback

        self.__tuner_mapping = KemperMappings.TUNER_MODE_STATE()
        self.register_mapping(self.__tuner_mapping)

    def enabled(self, action):
        if self.__tuner_mapping.value == 1:
            # Tuner enabled
            return False
        elif self.__enable_callback:
            return self.__enable_callback.enabled(action)
        else:
            return True
