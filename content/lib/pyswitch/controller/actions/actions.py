from micropython import const

from .Action import Action
from ...misc import PeriodCounter, get_option, Updater


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
        #self.set(self._state)
        
        if self.callback:
            self.callback.state_changed_by_user(self)

        self.update_displays()

    # Set functionality on or off (bool).
    #def set(self, state):
    #    pass                                                         # pragma: no cover

    # Update the state without functional changes. This is used to react to
    # parameters that have to be requested first. When the answer comes in, the state 
    # is set here again, but no functional update is done.
    def feedback_state(self, state):
        self._state = state

        self.update_displays()

    # Button pushed
    def push(self):
        if self._mode == self.ENABLE:
            # Enable
            self.state = True

        elif self._mode == self.DISABLE:
            # Disable
            self.state = False

        elif self._mode == self.LATCH:
            # Latch mode: Simply toggle states
            self.state = not self.state

        elif self._mode == self.MOMENTARY:
            # Momentary mode: Enable on push
            self.state = True

        elif self._mode == self.MOMENTARY_INVERSE:
            # Momentary mode: Enable on push
            self.state = False

        elif self._mode == self.HOLD_MOMENTARY:
            # Hold Momentary: Toggle like latch, and remember the current timestamp
            self._period.reset()
            self.state = not self.state

        elif self._mode == self.ONE_SHOT:
            self._state = False    # Triggers that set() is called by the state property in the next line
            self.state = True

    # Button released
    def release(self):
        if self._mode == self.MOMENTARY:
            self.state = False
        
        elif self._mode == self.MOMENTARY_INVERSE:
            self.state = True
        
        elif self._mode == self.HOLD_MOMENTARY:
            if self._period.exceeded:
                # Momentary if the period exceeded
                self.state = not self.state

        elif self._mode == self.ONE_SHOT:
            # Do not use the child classes set() method: We do not want an "off" message to be sent here.
            self.feedback_state(False)

    # Reset the action: Set False state without sending anything
    def reset(self):
        self.feedback_state(False)


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

    def update(self):
        Action.update(self)
        Updater.update(self)
        
    # Can return child actions (used for LED addressing)
    def get_all_actions(self):
        ret = [self]

        for a in self._actions:
            ret = ret + a.get_all_actions()

        for a in self._actions_hold:
            ret = ret + a.get_all_actions()

        return ret
    
    # Check if hold time exceeded
    def do_update(self):
        if self._active:
            self._check_hold()

    # Checks hold time and triggers hold action if exceeded.
    def _check_hold(self):
        if self._period_hold.exceeded:
            self._active = False

            # Hold click
            for action in self._actions_hold:
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

    # Applied to all sub-actions
    #def force_update(self):
    #    for action in self._actions:
    #        action.force_update()

    #    for action in self._actions_hold:
    #        action.force_update()

    # Applied to all sub-actions
    #def reset_display(self):
    #    for action in self._actions:
    #        action.reset_display()

    #    for action in self._actions_hold:
    #        action.reset_display()


################################################################################################################################


# Implements generic parameter switching on base of the PushButtonAction class
#class ParameterAction(PushButtonAction): #, ClientRequestListener):

#    # Comparison modes (for the valueEnable value when requesting a value)
#    EQUAL = const(0)                 # Enable when exactly the valueEnable value comes in
    
#    GREATER = const(10)              # Enable when a value greater than valueEnable comes in
#    GREATER_EQUAL = const(20)        # Enable when the valueEnable value comes in, or anything greater

#    LESS = const(30)                 # Enable when a value less than valueEnable comes in
#    LESS_EQUAL = const(40)           # Enable when the valueEnable value comes in, or anything less

#    NO_STATE_CHANGE = const(999)     # Do not receive any values

#    # Brightness values 
#    DEFAULT_LED_BRIGHTNESS_ON = 0.3
#    DEFAULT_LED_BRIGHTNESS_OFF = 0.02

#    # Dim factor for disabled effect slots (TFT display only)
#    DEFAULT_SLOT_DIM_FACTOR_ON = 1
#    DEFAULT_SLOT_DIM_FACTOR_OFF = 0.2

    # Generic MIDI parameter action.
    #
    # Additional options:
    # {
    #     "mode":                Mode of push button operation (see modes defined above). Optional, default is PushButtonModes.HOLD_MOMENTARY
    #
    #     "holdTimeMillis":      Optional hold time in milliseconds. Default is PushButtonModes.DEFAULT_LATCH_MOMENTARY_HOLD_TIME
    #
    #     "mapping":             A ClientParameterMapping instance. See mappings.py for some predeifined ones.
    #
    #     "mappingDisable":      Mapping to be used for disabling the action. 
    #
    #     "valueEnable":         Value to be sent as "enabled". Optional: Default is 1. If mapping.set is a list, this must
    #                            also be a list of values for the set messages in the mapping.
    #
    #     "valueDisable":        Value to be sent as "disabled". Optional: Default is 0. If mapping.set is a list, this must
    #                            also be a list of values for the set messages in the mapping.
    #                            SPECIAL: If you set this (or items of this) to "auto", the "disabled" value will be determined from the 
    #                            client's current parameter value when the action state is False (the old value is restored).
    #
    #     "referenceValue":      Optional: The value of incoming messages will be compared against this to determine state
    #                            (acc. to the comparison mode). If not set, "valueEnable" is used (first entry if valueEnabled is a list). 
    #
    #     "comparisonMode":      Mode of comparison when receiving a value. Default is ParameterActionModes.GREATER_EQUAL. 
    #
    #     "useSwitchLeds":       Use LEDs to visualize state. Optional, default is True.
    #
    #     "text":                Text (optional)
    #
    #     "textDisabled":        Text for diabled state (optional)
    #
    #     "displayDimFactor": {
    #         "on":              Dim factor in range [0..1] for on state (display label) Optional.
    #         "off":             Dim factor in range [0..1] for off state (display label) Optional.
    #     }
    #
    #     "ledBrightness": {
    #         "on":              LED brightness [0..1] for on state (Switch LEDs) Optional.
    #         "off":             LED brightness [0..1] for off state (Switch LEDs) Optional.
    #     }
    # }
#    def __init__(self, config = {}):
#        super().__init__(config)

#        self._current_display_state = -1
#        self._current_color = -1

#        # Per default, this uses the LEDs. You can switch that off however.
#        self.uses_switch_leds = get_option(config, "useSwitchLeds", True)

#        # Mapping(s)
#        self._mapping = config["mapping"]
#        self._mapping_off = get_option(config, "mappingDisable", None)

#        # Values
#        self._value_enable = get_option(config, "valueEnable", 1)                                # Can be an array
#        self._value_disable = get_option(config, "valueDisable", 0)                              # Can be an array
#        self._reference_value = get_option(config, "referenceValue", self._value_enable if not isinstance(self._value_enable, list) else self._value_enable[0]) 

#        # Auto mode for valueDisable
#        self._update_value_disabled = False
#        if not isinstance(self._value_disable, list):
#            self._update_value_disabled = (self._value_disable == "auto")
#        else:
#            self._update_value_disabled = [v == "auto" for v in self._value_disable]            

#        self._comparison_mode = get_option(config, "comparisonMode", self.GREATER_EQUAL)

#        # Text(s)
#        self._text = get_option(config, "text", False)
#        self._text_disabled = get_option(config, "textDisabled", False)

#        # Dim factors for displays
#        if get_option(config, "displayDimFactor") != False:
#            self._dim_factor_on = get_option(config["displayDimFactor"], "on", self.DEFAULT_SLOT_DIM_FACTOR_ON)
#            self._dim_factor_off = get_option(config["displayDimFactor"], "off", self.DEFAULT_SLOT_DIM_FACTOR_OFF)
#        else:
#            self._dim_factor_on = self.DEFAULT_SLOT_DIM_FACTOR_ON
#            self._dim_factor_off = self.DEFAULT_SLOT_DIM_FACTOR_OFF

#        # LED brightness settings
#        if get_option(config, "ledBrightness") != False:
#            self._brightness_on = get_option(config["ledBrightness"], "on", self.DEFAULT_LED_BRIGHTNESS_ON)
#            self._brightness_off = get_option(config["ledBrightness"], "off", self.DEFAULT_LED_BRIGHTNESS_OFF)
#        else:
#            self._brightness_on = self.DEFAULT_LED_BRIGHTNESS_ON
#            self._brightness_off = self.DEFAULT_LED_BRIGHTNESS_OFF

#    # Register all mappings
#    def init(self, appl, switch):
#        super().init(appl, switch)
        
#        self.appl.client.register(self._mapping, self)
        
#        if self._mapping_off:
#            self.appl.client.register(self._mapping_off, self)

#    # Set state (called by base class)
#    def set(self, enabled):        
#        if enabled:
#            set_mapping = self._mapping
#            value = self._value_enable
#        else:
#            if self._mapping_off:
#                set_mapping = self._mapping_off
#            else:
#                set_mapping = self._mapping

#            value = self._value_disable

#        if not isinstance(self._value_disable, list):
#            if value != "auto":
#                self.appl.client.set(set_mapping, value)
#        else:
#            auto_contained = False
#            for v in self._value_disable:
#                if v == "auto":
#                    auto_contained = True
#                    break
#            if not auto_contained:
#                self.appl.client.set(set_mapping, value)

#        # Request value
#        self._request_value()

#    # Request real state from controlled device
#    def do_update(self):
#        self._request_value()

#    # Request parameter value
#    def _request_value(self):
#        self.appl.client.request(self._mapping, self) #_request_mapping, self)

#    # Update display and LEDs to the current state
#    def update_displays(self):
#        if not self.enabled:
#            return

        # Callback. If it returns True, we are finished here.
        #if self._update_displays_callback and self._update_displays_callback.get((self, self._mapping)):
        #    self._current_color = self.color
        #    self._current_display_state = self.state
        #    return 
        
        # Set color, if new
#        if self.color != self._current_color:
#            self._current_color = self.color
        
#            self.set_switch_color(self.color)
#            self.set_label_color(self.color)
#            self._update_label_text()            
    
#        # Update when state have been changed
#        if self._current_display_state != self.state:
#            self._current_display_state = self.state

#            self.set_switch_color(self.color)
#            self.set_label_color(self.color)
#            self._update_label_text()

#    # Update switch brightness
#    def set_switch_color(self, color):
#        # Update switch LED color 
#        self.switch_color = color

#        if self.state == True:
#            # Switched on
#            self.switch_brightness = self._brightness_on
#        else:
#            # Switched off
#            self.switch_brightness = self._brightness_off

#    # Update label color, if any
#    def set_label_color(self, color):
#        if not self.label:
#            return
            
#        if self.state == True:
#            self.label.back_color = self._dim_color(color, self._dim_factor_on)
#        else:
#            self.label.back_color = self._dim_color(color, self._dim_factor_off)

#    # Update text if set
#    def _update_label_text(self):
#        if not self.label:
#            return
            
#        if self._text == False:
#            return
        
#        if self.state == True:
#            self.label.text = self._text
#        else:
#            if self._text_disabled != False:
#                self.label.text = self._text_disabled
#            else:
#                self.label.text = self._text

#    # Dims a passed color for display of disabled state
#    def _dim_color(self, color, factor):
#        if isinstance(color[0], tuple):
#            # Multi color
#            ret = []
#            for c in color:
#                ret.append((
#                    int(c[0] * factor),
#                    int(c[1] * factor),
#                    int(c[2] * factor)
#                ))
#            return ret
#        else:
#            # Single color
#            return (
#                int(color[0] * factor),
#                int(color[1] * factor),
#                int(color[2] * factor)
#            )
#
#    # Must reset all action states so the instance is being updated
#    def force_update(self):
#        self._current_display_state = -1
#        self._current_color = -1

#    # Must reset the displays
#    def reset_display(self):
#        if self.label:
#            self.label.text = ""
#            self.label.back_color = DEFAULT_LABEL_COLOR

#        self.switch_color = Colors.BLACK
#        self.switch_brightness = 0

#    # Called by the Client class when a parameter request has been answered
#    def parameter_changed(self, mapping):
#        if not self._mapping.response: 
#            return            
        
#        if mapping != self._mapping: 
#            return
        
#        state = False
        
#        if self._comparison_mode == self.EQUAL:
#            if mapping.value == self._reference_value:
#                state = True

#        elif self._comparison_mode == self.GREATER_EQUAL:
#            if mapping.value >= self._reference_value:
#                state = True

#        elif self._comparison_mode == self.GREATER:
#            if mapping.value > self._reference_value: 
#                state = True

#        elif self._comparison_mode == self.LESS_EQUAL:
#            if mapping.value <= self._reference_value:
#                state = True

#        elif self._comparison_mode == self.LESS:
#            if mapping.value < self._reference_value: 
#                state = True        

#        elif self._comparison_mode == self.NO_STATE_CHANGE:
#            state = self.state

#        else:
#            raise Exception() #"Invalid comparison mode: " + repr(self._comparison_mode))        

#        # Remember value for callback
#        self._mapping.value = mapping.value
#
#        self.feedback_state(state)        

#        # If enabled, remember the value for later when disabled
#        if state == True or not self._update_value_disabled:
#            return
        
#        if not isinstance(self._value_disable, list):
#            self._value_disable = mapping.value
#        else:
#            for i in range(len(self._value_disable)):
#                if self._update_value_disabled[i]:
#                    self._value_disable[i] = mapping.value

#    # Called when the client is offline (requests took too long)
#    def request_terminated(self, mapping):        
#        if mapping != self._mapping: 
#            return
        
#        self.state = False

#        self.update_displays()


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

