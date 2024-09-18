from .Action import Action
from ....Tools import Tools
from .....definitions import PushButtonModes


# Implements an abstraction layer for on/off parameters. Covers latch/momentary modes etc.
class PushButtonAction(Action):
    
    # config:
    # {
    #      "mode": Mode of operation (see PushButtonModes). Optional, default is PushButtonModes.HOLD_MOMENTARY,
    #      "holdTimeMillis": Optional hold time in milliseconds. Default is PushButtonModes.DEFAULT_LATCH_MOMENTARY_HOLD_TIME
    # }
    def __init__(self, appl, switch, config):
        super().__init__(appl, switch, config)

        self._mode = Tools.get_option(self.config, "mode", PushButtonModes.HOLD_MOMENTARY)
        self._hold_time_ms = Tools.get_option(self.config, "holdTimeMillis", PushButtonModes.DEFAULT_LATCH_MOMENTARY_HOLD_TIME)
        self._state = False
        self._start_time = 0

    @property
    def state(self):
        return self._state
    
    # Sets the state, also triggering the child class functionality. If you just 
    # want to set the state internally after feedback from the controlled device,
    # use feedback_state().
    @state.setter
    def state(self, state):
        self._state = state
        self.set(self._state)

    # Abstract: Set functionality on or off (bool).
    def set(self, state):
        raise Exception("Must be implemented by deriving classes")

    # Update the state without functional changes. This is used to react to
    # parameters that have to be requested first. When the answer comes in, the state 
    # is set again here, but no functional update is done.
    def feedback_state(self, state):
        self._state = state

    # Button pushed
    def push(self):
        if self._mode == PushButtonModes.ENABLE:
            # Enable
            self.state = True

        if self._mode == PushButtonModes.DISABLE:
            # Disable
            self.state = False

        if self._mode == PushButtonModes.LATCH:
            # Latch mode: Simply toggle states
            self.state = not self.state

        elif self._mode == PushButtonModes.MOMENTARY:
            # Momentary mode: Enable on push
            self.state = True

        elif self._mode == PushButtonModes.MOMENTARY_INVERSE:
            # Momentary mode: Enable on push
            self.state = False

        elif self._mode == PushButtonModes.HOLD_MOMENTARY:
            # Hold Momentary: Toggle like latch, and remember the current timestamp
            self._start_time = Tools.get_current_millis()
            self.state = not self.state

    # Button released
    def release(self):
        if self._mode == PushButtonModes.MOMENTARY:
            self.state = False
        
        if self._mode == PushButtonModes.MOMENTARY_INVERSE:
            self.state = True
        
        elif self._mode == PushButtonModes.HOLD_MOMENTARY:
            diff = Tools.get_current_millis() - self._start_time

            if diff >= self._hold_time_ms:
                self.state = not self.state


