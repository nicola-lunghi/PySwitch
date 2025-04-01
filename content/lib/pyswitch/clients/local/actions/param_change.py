from ....controller.actions import Action
from ....controller.callbacks import Callback
from ....misc import Colors

from adafruit_midi.system_exclusive import SystemExclusive


# Can be used for all parameter mappings: Increases or decreases the parameter value by a given offset. 
# 
# Optionally, the current value can be shown in a display label, and/or be previewed in another display label (the rig name for example).
def PARAMETER_UP_DOWN(mapping, 
                      offset,                            # Offset to be added to the parameter value. The range for this depends on whether the mapping's set message is a SysEx ([0..16383]) or ControlChange ([0..127]).
                      max_value = None,                  # Max. value. If None, this is derived automatically from the mapping (SysEx: 16383, CC: 127).
                      display = None,                    # Display label to show the value and color.
                      change_display = None,             # Can be assigned to an additonal display label which is used to show the changed values for a period of time.
                      change_timeout_millis = 1500,      # Amount of time the value is shown in the change display, if change_display is set.
                      text = "{val}%",                   # Text for the main display parameter's label. Can contain {val} which will be replaced with the current parameter value (percentage in range [0..100])
                      color = Colors.LIGHT_GREEN, 
                      id = False, 
                      use_leds = True,
                      led_brightness = 0.3,              # LED brightness for max value
                      enable_callback = None
    ):
    return Action({
        "callback": _ParameterChangeCallback(
            mapping = mapping,
            offset = offset,
            max_value = max_value,
            text = text,
            color = color,
            led_brightness = led_brightness,
            change_display = change_display,
            change_timeout_millis = change_timeout_millis
        ),
        "display": display,
        "id": id,
        "useSwitchLeds": use_leds,
        "enableCallback": enable_callback
    })

class _ParameterChangeCallback(Callback):

    def __init__(self,
                 mapping, 
                 offset,
                 max_value,
                 color, 
                 text, 
                 led_brightness,
                 change_display,
                 change_timeout_millis
        ):
        super().__init__(mappings = [mapping])

        self._mapping = mapping
        self._offset = offset
        self._max_value = max_value
        self._led_brightness = led_brightness
        self._color = color
        self._text = text
        
        if change_display:
            from ....controller.preview import ValuePreview

            self.__preview = ValuePreview.get(change_display)
            self.__change_timeout_millis = change_timeout_millis
        else:
            self.__preview = None

        if self._max_value == None:
            if isinstance(mapping.set, SystemExclusive):
                self._max_value = 16383
            else:
                self._max_value = 127
    
    def init(self, appl, listener = None):
        super().init(appl, listener)

        self.__appl = appl

    def update(self):
        super().update()

        if self.__preview:
            self.__preview.update()

    def push(self):
        v = self._mapping.value + self._offset

        if v < 0:
            v = 0
        if v > self._max_value:
            v = self._max_value
        
        self.__appl.client.set(self._mapping, v)

        if self.__preview:
            self.__preview.preview_mapping(
                mapping = self._mapping,
                value = v,
                max_value = self._max_value,
                timeout_millis = self.__change_timeout_millis
            )

    def release(self):
        pass

    def update_displays(self):
        dim_factor = (self._mapping.value / self._max_value) if self._mapping.value != None else 0

        if self.action.label:
            if self.action.label.back_color:
                self.action.label.back_color = (
                    int(self._color[0] * dim_factor),
                    int(self._color[1] * dim_factor),
                    int(self._color[2] * dim_factor)
                )

            if self._mapping.value != None:
                val = str(round(self._mapping.value * 100 / self._max_value))
            else:
                val = '?'

            self.action.label.text = self._text.replace("{val}", val)

        self.action.switch_color = self._color
        self.action.switch_brightness = dim_factor * self._led_brightness

