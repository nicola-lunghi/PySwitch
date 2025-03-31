from ....controller.actions import PushButtonAction
from ....controller.callbacks import BinaryParameterCallback
from ....misc import Colors
from adafruit_midi.system_exclusive import SystemExclusive


# Generic switch action which can be used for all parameter mappings
def PARAMETER_UP_DOWN(mapping, 
                      offset,                  # Offset to be added to the parameter value
                      max_value = None,        # Max. value. If None, this is derived automatically from the mapping.
                      display = None, 
                      text = "",               # Can contain {val} which will be replaced with the current parameter value
                      color = Colors.LIGHT_GREEN, 
                      id = False, 
                      use_leds = True,
                      led_brightness = 0.3,    # LED brightness for max value
                      enable_callback = None
    ):
    return PushButtonAction({
        "callback": _RotateParameterCallback(
            mapping = mapping,
            offset = offset,
            max_value = max_value,
            text = text,
            color = color,
            led_brightness = led_brightness
        ),
        "mode": PushButtonAction.LATCH,
        "display": display,
        "id": id,
        "useSwitchLeds": use_leds,
        "enableCallback": enable_callback
    })

class _RotateParameterCallback(BinaryParameterCallback):

    def __init__(self,
                 mapping, 
                 offset,
                 max_value,
                 color, 
                 text, 
                 led_brightness
        ):
        super().__init__(mapping = mapping, color = color, text = text)

        self._offset = offset
        self._max_value = max_value
        self._led_brightness = led_brightness

        if self._max_value == None:
            if isinstance(mapping.set, SystemExclusive):
                self._max_value = 16383
            else:
                self._max_value = 127
    
    def init(self, appl, listener = None):
        super().init(appl, listener)

        self.__appl = appl

    def state_changed_by_user(self):
        v = self.mapping.value + self._offset

        if v < 0:
            v = 0
        if v > self._max_value:
            v = self._max_value
        
        self.__appl.client.set(self.mapping, v)

    def update_displays(self):
        dim_factor = (self.mapping.value / self._max_value) if self.mapping.value != None else 0

        if self.action.label:
            if self.action.label.back_color:
                self.action.label.back_color = (
                    self._color[0] * dim_factor,
                    self._color[1] * dim_factor,
                    self._color[2] * dim_factor
                )

            if self.mapping.value != None:
                self.action.label.text = self._text.replace("{val}", str(round(self.mapping.value * 100 / self._max_value)))
            else:
                self.action.label.text = self._text

        self.action.switch_color = self._color
        self.action.switch_brightness = dim_factor * self._led_brightness

    def evaluate_value(self, value):
        pass
