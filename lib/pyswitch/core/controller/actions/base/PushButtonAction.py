from .Action import Action
from ....misc.Tools import Tools

# Modes for PushButtonAction
class PushButtonModes:    
    ENABLE = 0                      # Switch the functionality on
    DISABLE = 10                    # Switch the functionality off
    LATCH = 20                      # Toggle state on every button push
    MOMENTARY = 30                  # Enable on push, disable on release
    MOMENTARY_INVERSE = 40          # Disable on push, Enable on release
    HOLD_MOMENTARY = 50             # Combination of latch, momentary and momentary inverse: If pushed shortly, latch mode is 
                                    # used. If pushed longer than specified in the "holdTimeMillis" parameter, momentary mode is 
                                    # used (inverse or not: This depends on the current state of the functionality. When it is
                                    # on, it will momentarily be switched off and vice versa).
    ONE_SHOT = 100                  # Fire the SET command on every push (show as disabled)

    # Hold time for HOLD_MOMENTARY mode (milliseconds)
    DEFAULT_LATCH_MOMENTARY_HOLD_TIME = 600  


################################################################################################################################


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
        if state == self._state:
            return
        
        self._state = state
        self.set(self._state)

        self.update_displays()

    # Abstract: Set functionality on or off (bool).
    def set(self, state):
        raise Exception("Must be implemented by deriving classes")

    # Update the state without functional changes. This is used to react to
    # parameters that have to be requested first. When the answer comes in, the state 
    # is set again here, but no functional update is done.
    def feedback_state(self, state):
        self._state = state

        self.update_displays()

    # Button pushed
    def push(self):
        if self._mode == PushButtonModes.ENABLE:
            # Enable
            self.state = True

        elif self._mode == PushButtonModes.DISABLE:
            # Disable
            self.state = False

        elif self._mode == PushButtonModes.LATCH:
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

        elif self._mode == PushButtonModes.ONE_SHOT:
            self._state = False    # Triggers that set() is called by the state property in the next line
            self.state = True

    # Button released
    def release(self):
        if self._mode == PushButtonModes.MOMENTARY:
            self.state = False
        
        elif self._mode == PushButtonModes.MOMENTARY_INVERSE:
            self.state = True
        
        elif self._mode == PushButtonModes.HOLD_MOMENTARY:
            diff = Tools.get_current_millis() - self._start_time

            if diff >= self._hold_time_ms:
                self.state = not self.state

        elif self._mode == PushButtonModes.ONE_SHOT:
            # Do not use the child classes set() method: We do not want an "off" message to be sent here.
            self.feedback_state(False)

    # Reset the action: Set False state without sending anything
    def reset(self):
        if self.debug:
            Tools.print(" -> Reset action")
            
        self.feedback_state(False)
