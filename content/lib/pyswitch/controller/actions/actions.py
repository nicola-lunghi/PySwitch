from micropython import const

from .Action import Action
from ...misc import PeriodCounter, get_option, Updater
#from ...stats import RuntimeStatistics

# Implements an abstraction layer for on/off parameters. Covers latch/momentary modes etc.
class PushButtonAction(Action):
    
    ENABLE = const(0)                      # Switch the functionality on
    DISABLE = const(10)                    # Switch the functionality off
    LATCH = const(20)                      # Toggle state on every button push
    MOMENTARY = const(30)                  # Enable on push, disable on release
    MOMENTARY_INVERSE = const(40)          # Disable on push, Enable on release
    HOLD_MOMENTARY = const(50)             # Combination of latch, momentary and momentary inverse: If pushed shortly, latch mode is 
                                           # used. If pushed longer than specified in the "holdTimeMillis" parameter, momentary mode is 
                                           # used (inverse or not: This depends on the current state of the functionality. When it is
                                           # on, it will momentarily be switched off and vice versa).
    ONE_SHOT = const(100)                  # Fire the SET command on every push (show as disabled)

    # Hold time for HOLD_MOMENTARY mode (milliseconds)
    DEFAULT_LATCH_MOMENTARY_HOLD_TIME = const(600)

    # config:
    # {
    #      "callback":        The callback has to additionally implement the function state_changed_by_user(action).
    #      "mode":            Mode of operation (see PushButtonModes). Optional, default is HOLD_MOMENTARY,
    #      "holdTimeMillis":  Optional hold time in milliseconds. Default is DEFAULT_LATCH_MOMENTARY_HOLD_TIME
    # }
    def __init__(self, config = {}, period_counter = None):
        super().__init__(config)

        self._mode = get_option(config, "mode", self.HOLD_MOMENTARY)
        
        self._period = period_counter
        if not self._period:
            hold_time_ms = get_option(config, "holdTimeMillis", self.DEFAULT_LATCH_MOMENTARY_HOLD_TIME)
            self._period = PeriodCounter(hold_time_ms)
        
        self._state = False

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
        
        if self.callback:
            self.callback.state_changed_by_user(self)

        self.update_displays()

    # Update the state without functional changes. This is used to react to
    # parameters that have to be requested first. When the answer comes in, the state 
    # is set here again, but no functional update is done.
    def feedback_state(self, state):
        self._state = state

    # Button pushed
    def push(self):
        mode = self._mode

        if mode == self.ENABLE:
            # Enable
            self.state = True

        elif mode == self.DISABLE:
            # Disable
            self.state = False

        elif mode == self.LATCH:
            # Latch mode: Simply toggle states
            self.state = not self.state

        elif mode == self.MOMENTARY:
            # Momentary mode: Enable on push
            self.state = True

        elif mode == self.MOMENTARY_INVERSE:
            # Momentary mode: Enable on push
            self.state = False

        elif mode == self.HOLD_MOMENTARY:
            # Hold Momentary: Toggle like latch, and remember the current timestamp
            self._period.reset()
            self.state = not self.state

        elif mode == self.ONE_SHOT:
            self._state = False    # Triggers that set() is called by the state property in the next line
            self.state = True

    # Button released
    def release(self):
        mode = self._mode

        if mode == self.MOMENTARY:
            self.state = False
        
        elif mode == self.MOMENTARY_INVERSE:
            self.state = True
        
        elif mode == self.HOLD_MOMENTARY:
            if self._period.exceeded:
                # Momentary if the period exceeded
                self.state = not self.state

        elif mode == self.ONE_SHOT:
            # Do not use the child classes set() method: We do not want an "off" message to be sent here.
            self._state = False
            self.update_displays()

    # Reset the action: Set False state without sending anything
    def reset(self):
        self._state = False
        self.update_displays()


################################################################################################################################


# Implements an abstraction layer for triggering different actions on hold/double click
class HoldAction(Action, Updater):

    # Default hold time
    DEFAULT_HOLD_TIME_MILLIS = const(600)            

    # config:
    # {
    #      "actions":               Default list of actions (can be conditional). Mandatory.
    #      "actionsHold":           List of actions to perform on holding the switch (can be conditional). Optional.
    #      "holdTimeMillis":        Optional hold time in milliseconds. Default is DEFAULT_HOLD_TIME_MILLIS.
    #                               Note that the sensing here is done only every processing update interval!
    # }
    def __init__(self, config = {}, period_counter_hold = None):
        Action.__init__(self, config)
        Updater.__init__(self)
        
        self._active = False

        self._actions = get_option(config, "actions", [])
        self._actions_hold = get_option(config, "actionsHold", [])

        # Hold period counter
        self._period_hold = period_counter_hold
        if not self._period_hold:
            hold_time_ms = get_option(config, "holdTimeMillis", self.DEFAULT_HOLD_TIME_MILLIS)
            self._period_hold = PeriodCounter(hold_time_ms)
        
    # Set up action instances
    def init(self, appl, switch):
        super().init(appl, switch)

        for action in self._actions + self._actions_hold:
            action.init(appl, switch)        
            self.add_updateable(action)    

    #@RuntimeStatistics.measure
    def update(self):
        Action.update(self)
        Updater.update(self)

        if self._active and self.enabled:
            self._check_hold()
        
    # Can return child actions (used for LED addressing)
    def get_all_actions(self):
        ret = [self]

        for a in self._actions:
            ret = ret + a.get_all_actions()

        for a in self._actions_hold:
            ret = ret + a.get_all_actions()

        return ret
    
    # Checks hold time and triggers hold action if exceeded.
    def _check_hold(self):
        if self._period_hold.exceeded:
            self._active = False

            # Hold click
            for action in self._actions_hold:
                if not action.enabled:
                    continue

                action.push()        
                action.release()

            return True
        
        return False
    
    # Button pushed: Here, we just reset the period for hold, all processing takes 
    # place in the release() method
    def push(self):     
        self._period_hold.reset()
        self._active = True

    # Button released
    def release(self):
        if not self._active:
            return
        
        if self._check_hold():
            return

        # Normal click
        for action in self._actions:
            if not action.enabled:
                continue
            
            action.push()        
            action.release()

        self._active = False

    # Applied to all sub-actions
    def update_displays(self):
        super().update_displays()

        for action in self._actions:
            action.update_displays()

        for action in self._actions_hold:
            action.update_displays()

    # Applied to all sub-actions
    def reset(self):
        for action in self._actions:
            action.reset()

        for action in self._actions_hold:
            action.reset()


################################################################################################################################


# Reset displays
class ResetDisplaysAction(Action):    
    
    # Used to reset the screen areas which show rig info details directly after rig changes.
    # Additional options:
    # {
    #     "resetSwitches":        Reset switches (including LEDs and display labels, if assigned) (optional)
    #     "ignoreOwnSwitch":      Do not reset the switch this action is assigned to (optional)
    #     "resetDisplayAreas":    Reset display areas (optional)
    # }
    def __init__(self, config = {}):
        super().__init__(config)
                
        self._reset_switches = get_option(config, "resetSwitches")
        self._ignore_own_switch = get_option(config, "ignoreOwnSwitch")
        self._reset_display_areas = get_option(config, "resetDisplayAreas")

    def push(self):
        if self._reset_switches:
            if self._ignore_own_switch:
                self.appl.reset_switches([self.switch])
            else:
                self.appl.reset_switches()

        if self._reset_display_areas:
            self.appl.reset_display_areas()

