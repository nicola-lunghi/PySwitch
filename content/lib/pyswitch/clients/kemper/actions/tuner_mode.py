from ....controller.actions import PushButtonAction
from ....controller.callbacks import BinaryParameterCallback
from ...kemper import KemperMappings
from ....misc import Colors, DEFAULT_SWITCH_COLOR

# Switch tuner mode on / off
def TUNER_MODE(display = None, mode = PushButtonAction.HOLD_MOMENTARY, color = DEFAULT_SWITCH_COLOR, text = "Tuner", id = False, use_leds = True, enable_callback = None):
    return PushButtonAction({
        "callback": _TunerModeCallback(
            text = text,
            color = color
        ),
        "mode": mode,   
        "display": display,            
        "id": id,
        "useSwitchLeds": use_leds,
        "enableCallback": enable_callback
    })


# Callback for tuner mode
class _TunerModeCallback(BinaryParameterCallback):
    def __init__(self, color, text):
        self.__mapping = KemperMappings.TUNER_MODE_STATE()
        super().__init__(
            mapping = self.__mapping,
            comparison_mode = BinaryParameterCallback.EQUAL,
            text = text,
            color = color
        )

        self.__just_clicked = False

    def init(self, appl, listener = None):
        super().init(appl, listener)
        self.__appl = appl

    def state_changed_by_user(self, action):
        # Code from BinaryParameterCallback.state_changed_by_user (implemented here directly to reduce stack size)
        self.__appl.client.set(self.__mapping, self._value_enable if action.state else self._value_disable)
        
        # Request value
        self.update()
        
        self.__just_clicked = True

    def parameter_changed(self, mapping):
        super().parameter_changed(mapping)
        
        if mapping != self.__mapping:
            return
        
        if self.__mapping.value == 1:
            # Tuner on
            for switch in self.__appl.switches:
                switch.override_action = self
                
                switch.color = Colors.WHITE
                switch.brightness = self._led_brightness_off
        else:
            # Tuner off
            for switch in self.__appl.switches:
                switch.override_action = None

                for action in switch.actions:
                    action.reset()

    def push(self):
        pass

    def release(self):
        if self.__just_clicked:
            # This prevents that the tuner button switches off the tuner immediately at releasing 
            self.__just_clicked = False
            return
        
        self.__appl.client.set(self.__mapping, 0)  