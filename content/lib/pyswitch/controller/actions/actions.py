from .Action import Action
from ..Client import ClientParameterMapping
from ...misc import Tools, Defaults, Colors, PeriodCounter
from ..ConditionTree import ConditionTree


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
    def __init__(self, config = {}, period_counter = None):
        super().__init__(config)

        self._mode = Tools.get_option(self.config, "mode", PushButtonModes.HOLD_MOMENTARY)
        
        self._period = period_counter
        if not self._period:
            hold_time_ms = Tools.get_option(self.config, "holdTimeMillis", PushButtonModes.DEFAULT_LATCH_MOMENTARY_HOLD_TIME)
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
        self.set(self._state)

        self.update_displays()

    # Abstract: Set functionality on or off (bool).
    def set(self, state):
        raise Exception("Must be implemented by deriving classes")  # pragma: no cover

    # Update the state without functional changes. This is used to react to
    # parameters that have to be requested first. When the answer comes in, the state 
    # is set here again, but no functional update is done.
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
            self._period.reset()
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
            if self._period.exceeded:
                # Momentary if the period exceeded
                self.state = not self.state

        elif self._mode == PushButtonModes.ONE_SHOT:
            # Do not use the child classes set() method: We do not want an "off" message to be sent here.
            self.feedback_state(False)

    # Reset the action: Set False state without sending anything
    def reset(self):
        self.feedback_state(False)


################################################################################################################################


# Implements an abstraction layer for triggering different actions on hold/double click
class HoldAction(Action):
    
    DEFAULT_HOLD_TIME_MILLIS = 600            # Default hold time

    # config:
    # {
    #      "actions":               Default list of actions (can be conditional). Mandatory.
    #      "actionsHold":           List of actions to perform on holding the switch (can be conditional). Optional.
    #      "holdTimeMillis":        Optional hold time in milliseconds. Default is PushButtonMultiModes.DEFAULT_HOLD_TIME_MILLIS.
    #                               Note that the sensing here is done only every processing update interval!
    # }
    def __init__(self, config = {}, period_counter_hold = None):
        super().__init__(config)
        
        self._action_tree = None
        self._action_hold_tree = None
        self._active = False

        # Hold period counter
        self._period_hold = period_counter_hold
        if not self._period_hold:
            hold_time_ms = Tools.get_option(self.config, "holdTimeMillis", self.DEFAULT_HOLD_TIME_MILLIS)
            self._period_hold = PeriodCounter(hold_time_ms)
        
    # Tie the enabled state of the actions to the one of this action
    @Action.enabled.setter
    def enabled(self, value):
        Action.enabled.fset(self, value)

        self.condition_changed(None)

    # Set up action instances
    def init(self, appl, switch):
        super().init(appl, switch)

        self._action_tree = self._init_actions(appl, switch, Tools.get_option(self.config, "actions", []))
        self._action_hold_tree = self._init_actions(appl, switch, Tools.get_option(self.config, "actionsHold", []))

        # Update actions to initialize the correct initial state
        self.condition_changed(None)

        self.update_displays()

    # Initialize actions for a list
    def _init_actions(self, appl, switch, action_definitions):
        action_tree = ConditionTree(
            subject = action_definitions,
            listener = self
        )

        action_tree.init(appl)
        actions = action_tree.entries

        for action in actions:
            action.init(appl, switch)        
            appl.add_updateable(action)            
            #action.update_displays()

        return action_tree
        
    # Called on condition changes. The yes value will be True or False.
    def condition_changed(self, condition):
        self._actions = self._action_tree.values
        self._actions_hold = self._action_hold_tree.values

        all = self._action_tree.entries + self._action_hold_tree.entries
        
        if not self.enabled:
            for action in all:
                action.reset_display()
                action.enabled = False
            return

        active_actions = self._actions + self._actions_hold        

        to_disable = [a for a in all if a.enabled and not a in active_actions]
        to_enable = [a for a in all if not a.enabled and a in active_actions]

        # Execute the two lists in the correct order
        for action in to_disable:
            action.reset_display()
            action.enabled = False

        for action in to_enable:
            action.enabled = True

    # Can return child actions (used for LED addressing)
    def get_all_actions(self):
        ret = [self]

        for a in self._action_tree.entries:
            ret = ret + a.get_all_actions()

        for a in self._action_hold_tree.entries:
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
    def force_update(self):
        for action in self._actions:
            action.force_update()

        for action in self._actions_hold:
            action.force_update()

    # Applied to all sub-actions
    def reset_display(self):
        for action in self._actions:
            action.reset_display()

        for action in self._actions_hold:
            action.reset_display()


################################################################################################################################


# Comparison modes (for the valueEnabled value when requesting a value)
class ParameterActionModes:
    EQUAL = 0            # Enable when exactly the valueEnabled value comes in
    
    GREATER = 10         # Enable when a value greater than valueEnabled comes in
    GREATER_EQUAL = 20   # Enable when the valueEnabled value comes in, or anything greater

    LESS = 30            # Enable when a value less than valueEnabled comes in
    LESS_EQUAL = 40      # Enable when the valueEnabled value comes in, or anything less


################################################################################################################################


# Implements bipolar parameters on base of the PushButtonAction class
class ParameterAction(PushButtonAction): #, ClientRequestListener):

    # Brightness values 
    DEFAULT_LED_BRIGHTNESS_ON = 0.3
    DEFAULT_LED_BRIGHTNESS_OFF = 0.02

    # Dim factor for disabled effect slots (TFT display only)
    DEFAULT_SLOT_DIM_FACTOR_ON = 1
    DEFAULT_SLOT_DIM_FACTOR_OFF = 0.2

    # Generic MIDI parameter
    # Additional options:
    # {
    #     "mode":                Mode of operation (see PushButtonModes). Optional, default is PushButtonModes.HOLD_MOMENTARY,
    #     "holdTimeMillis":      Optional hold time in milliseconds. Default is PushButtonModes.DEFAULT_LATCH_MOMENTARY_HOLD_TIME
    #
    #     "mapping":             A ClientParameterMapping instance. See mappings.py for some predeifined ones.
    #                            This can also be an array: In this case the mappings are processed in the given order.
    #     "mappingDisable":      Mapping to be used on disabling the state. If mapping is an array, this has also to be an array.
    #
    #     "text":                Text (optional)
    #     "comparisonMode":      Mode of comparison when receiving a value. Default is ParameterActionModes.GREATER_EQUAL.    
    #     "useSwitchLeds":       Use LEDs to visualize state. Optional, default is True
    #
    #     "color":               Color for switch and display (optional, default: white). Can be either one color or a tuple of colors
    #                            with one color for each LED segment of the switch (if more actions share the LEDs, only the first
    #                            color is used)
    #
    #     "valueEnabled":        Value to be interpreted as "enabled". Optional: Default is 1. If mapping is a list, this must
    #                            also be a list of values for the mappings.
    #     "valueDisabled":       Value to be interpreted as "disabled". Optional: Default is 0. If mappingDisable (if provided)
    #                            or mapping is a list, this must also be a list of values for the mappings.
    #
    #     "setValueEnabled":     Optional: Value for setting. valueEnabled is only used for receiving if this is set.
    #     "setValueDisabled":    Optional: Value for setting. valueDisabled is only used for receiving if this is set.
    #
    #     "displayDimFactorOn":  Dim factor in range [0..1] for on state (display label)
    #     "displayDimFactorOff": Dim factor in range [0..1] for off state (display label)
    # }
    def __init__(self, config = {}):
        super().__init__(config)

        self.uses_switch_leds = Tools.get_option(self.config, "useSwitchLeds", True)

        # Action config
        self.color = Tools.get_option(self.config, "color", Defaults.DEFAULT_SWITCH_COLOR)
        
        self._mapping = self.config["mapping"]                                                          # Can be an array
        self._mapping_off = Tools.get_option(self.config, "mappingDisable", None)                       # Can be an array
        self._value_on = Tools.get_option(self.config, "valueEnabled", 1)                               # Can be an array
        self._value_off = Tools.get_option(self.config, "valueDisabled", 0)                             # Can be an array
        self._set_value_on = Tools.get_option(self.config, "setValueEnabled", self._value_on)           # Can be an array
        self._set_value_off = Tools.get_option(self.config, "setValueDisabled", self._value_off)        # Can be an array
        
        self._comparison_mode = Tools.get_option(self.config, "comparisonMode", ParameterActionModes.GREATER_EQUAL)

        self._text = Tools.get_option(self.config, "text", False)
        self._text_disabled = Tools.get_option(self.config, "textDisabled", False)

        self._get_request_mapping()        

        self._current_display_status = -1
        self._current_color = -1

    def init(self, appl, switch):
        super().init(appl, switch)

        # Global config
        self._dim_factor_on = Tools.get_option(
            self.config, "displayDimFactorOn", 
            Tools.get_option(
                self.appl.config, 
                "displayDimFactorOn", 
                self.DEFAULT_SLOT_DIM_FACTOR_ON
            )
        )
        self._dim_factor_off = Tools.get_option(
            self.config, "displayDimFactorOff", 
            Tools.get_option(
                self.appl.config, 
                "displayDimFactorOff", 
                self.DEFAULT_SLOT_DIM_FACTOR_OFF
            )
        )

        if Tools.get_option(self.config, "ledBrightness") != False:
            self._brightness_on = Tools.get_option(self.config["ledBrightness"], "on", self.DEFAULT_LED_BRIGHTNESS_ON)
            self._brightness_off = Tools.get_option(self.config["ledBrightness"], "off", self.DEFAULT_LED_BRIGHTNESS_OFF)
        elif Tools.get_option(self.appl.config, "ledBrightness") != False:
            self._brightness_on = Tools.get_option(self.appl.config["ledBrightness"], "on", self.DEFAULT_LED_BRIGHTNESS_ON)
            self._brightness_off = Tools.get_option(self.appl.config["ledBrightness"], "off", self.DEFAULT_LED_BRIGHTNESS_OFF)
        else:
            self._brightness_on = self.DEFAULT_LED_BRIGHTNESS_ON
            self._brightness_off = self.DEFAULT_LED_BRIGHTNESS_OFF

        # Register all mappings
        if isinstance(self._mapping, ClientParameterMapping):
            self.appl.client.register(self._mapping, self)
        else:
            for m in self._mapping:
                self.appl.client.register(m, self)
        
        if self._mapping_off:
            if isinstance(self._mapping_off, ClientParameterMapping):
                self.appl.client.register(self._mapping_off, self)
            else:
                for m in self._mapping_off:
                    self.appl.client.register(m, self)

    # Set state (called by base class)
    def set(self, enabled):        
        # Get mappings to execute
        mapping_definitions = self._get_set_mappings(enabled)

        for mapping_def in mapping_definitions:
            self.appl.client.set(mapping_def["mapping"], mapping_def["value"])
            
        # Request value
        self._request_value()

    # Request real state from controlled device
    def do_update(self):
        self._request_value()

    # Cancel eventually pending requests (which might return outdated values)
    # Request parameter value
    def _request_value(self):
        if not self._request_mapping:
            return            
        
        self.appl.client.request(self._request_mapping, self)

    # Update display and LEDs to the current state
    def update_displays(self):
        if not self.enabled:
            return

        # Set color, if new
        if self.color != self._current_color:
            self._current_color = self.color
        
            self.set_switch_color(self.color)
            self.set_label_color(self.color)
            self._update_label_text()
    
        # Only update when state have been changed
        if self._current_display_status != self.state:
            self._current_display_status = self.state

            self.set_switch_color(self.color)
            self.set_label_color(self.color)
            self._update_label_text()

    # Update switch brightness
    def set_switch_color(self, color):
        # Update switch LED color 
        self.switch_color = color

        if self.state == True:
            # Switched on
            self.switch_brightness = self._brightness_on
        else:
            # Switched off
            self.switch_brightness = self._brightness_off

    # Update label color, if any
    def set_label_color(self, color):
        if not self.label:
            return
            
        if self.state == True:
            self.label.back_color = self._dim_color(color, self._dim_factor_on)
        else:
            self.label.back_color = self._dim_color(color, self._dim_factor_off)

    # Update text if set
    def _update_label_text(self):
        if not self.label:
            return
            
        if self._text == False:
            return
        
        if self.state == True:
            self.label.text = self._text
        else:
            if self._text_disabled != False:
                self.label.text = self._text_disabled
            else:
                self.label.text = self._text

    # Dims a passed color for display of disabled state
    def _dim_color(self, color, factor):
        if isinstance(color[0], tuple):
            # Multi color
            ret = []
            for c in color:
                ret.append((
                    int(c[0] * factor),
                    int(c[1] * factor),
                    int(c[2] * factor)
                ))
            return ret
        else:
            # Single color
            return (
                int(color[0] * factor),
                int(color[1] * factor),
                int(color[2] * factor)
            )

    # For a given state, returns the mappings array to call set() on.
    def _get_set_mappings(self, state):
        # We can have differing mappings for enabled and disabled state.
        if state == True:
            candidates = self._mapping
        else:
            if self._mapping_off:
                candidates = self._mapping_off
            else:
                candidates = self._mapping

        # Get array of mappings to execute
        value_on = self._set_value_on
        value_off = self._set_value_off

        if isinstance(candidates, ClientParameterMapping):
            all = [candidates]

            if state == True:
                values = [value_on]
            else:
                values = [value_off]
        else:
            all = candidates

            if state == True:
                values = value_on
            else:
                values = value_off

        ret = []
        for i in range(len(all)):
            m = all[i]

            if not m.can_set:
                continue

            ret.append({
                "mapping": m,
                "value": values[i]
            })

        return ret

    # Get the mapping to be used for reuqesting values. This is the first one which is able to request. 
    def _get_request_mapping(self):
        self._request_mapping_value_on = None
        self._request_mapping = None

        if isinstance(self._mapping, ClientParameterMapping):
            # Mapping instance: Check if it can receive values
            if self._mapping.can_receive:
                self._request_mapping_value_on = self._value_on
                self._request_mapping = self._mapping
        else:
            # Array of mappings: Use the first one capable of receiving values
            for i in range(len(self._mapping)):
                mapping = self._mapping[i]

                if mapping.can_receive:
                    self._request_mapping = mapping
                    self._request_mapping_value_on = self._value_on[i]
                    break

    # Must reset all action states so the instance is being updated
    def force_update(self):
        self._current_display_status = -1
        self._current_color = -1

    # Must reset the displays
    def reset_display(self):
        if self.label:
            self.label.text = ""
            self.label.back_color = Defaults.DEFAULT_LABEL_COLOR

        self.switch_color = Colors.BLACK
        self.switch_brightness = 0

    # Called by the Client class when a parameter request has been answered
    def parameter_changed(self, mapping):
        #if not self.enabled:
        #    return
         
        if not self._request_mapping:
            return            
        
        if mapping != self._request_mapping:
            return
        
        state = False
        
        if self._comparison_mode == ParameterActionModes.EQUAL:
            if mapping.value == self._request_mapping_value_on:
                state = True

        elif self._comparison_mode == ParameterActionModes.GREATER_EQUAL:
            if mapping.value >= self._request_mapping_value_on:
                state = True

        elif self._comparison_mode == ParameterActionModes.GREATER:
            if mapping.value > self._request_mapping_value_on:
                state = True

        elif self._comparison_mode == ParameterActionModes.LESS_EQUAL:
            if mapping.value <= self._request_mapping_value_on:
                state = True

        elif self._comparison_mode == ParameterActionModes.LESS:
            if mapping.value < self._request_mapping_value_on:
                state = True        
        else:
            raise Exception("Invalid comparison mode: " + repr(self._comparison_mode))        

        if self.debug:  # pragma: no cover
            self.print(" -> Receiving binary switch status " + repr(mapping.value) + ", counted as " + repr(state))

        self.feedback_state(state)

    # Called when the client is offline (requests took too long)
    def request_terminated(self, mapping):
        if not self._request_mapping:
            return        
        
        if mapping != self._request_mapping:
            return
        
        if self.debug:  # pragma: no cover
            self.print(" -> Terminated request for parameter value, is the device offline?")
        
        self.state = False

        self.update_displays()


################################################################################################################################


# Implements the effect enable/disable footswitch action
class EffectEnableAction(ParameterAction): #, ClientRequestListener):
    
    # Switches an effect on/off, if the slot is assigned. Based on ParameterAction, so all options there
    # are available here, too.
    # 
    # Additional options:
    # {
    #     "slotInfo":       SlotInfoProvider
    #     "mapping":        A ClientParameterMapping instance to determine the effect status (on/off). 
    #                       Here, this cannot be an array!
    #     "mappingType":    A ClientParameterMapping instance to determine the effect type. 
    #     "categories":     A EffectCategoryProvider instance to determine the colors and names of the effect types.
    #     "mode":           Mode of operation (see PushButtonModes). Optional, default is PushButtonModes.HOLD_MOMENTARY,
    #     "holdTimeMillis": Optional hold time in milliseconds. Default is PushButtonModes.DEFAULT_LATCH_MOMENTARY_HOLD_TIME
    # }
    def __init__(self, config = {}):
        super().__init__(config)

        # Mapping for effect type
        self._mapping_fxtype = self.config["mappingType"] 

        # Slot info provider of type SlotInfoProvider
        self._slot_info = self.config["slotInfo"]
        
        # Category provider of type EffectCategoryProvider
        self._categories = self.config["categories"]
        
        self._effect_category = self._categories.get_category_not_assigned()  
        self._current_category = -1

    # Initialize the action
    def init(self, appl, switch):
        super().init(appl, switch)
        
        self._debug_slot_names = Tools.get_option(self.appl.config, "showEffectSlotNames", False)

        self.appl.client.register(self._mapping_fxtype, self)

    # Request effect type periodically (which itself will trigger a status request).
    # Does not call super.do_update because the status is requested here later anyway.
    def do_update(self):
        if not self._mapping_fxtype.can_receive:
            raise Exception("Mapping for effect type must be able to receive (provide request and response)")       
        
        if self.debug:   # pragma: no cover
            self.print("Request type")

        self.appl.client.request(self._mapping_fxtype, self)

    # Update display and LEDs to the current state and effect category
    def update_displays(self):
        if not self.enabled:
            super().update_displays()
            return
        
        # Only update when category of state have been changed
        if self._current_category == self._effect_category:
            super().update_displays()
            return
        
        self._current_category = self._effect_category

        # Effect category color
        self.color = self._categories.get_effect_category_color(self._effect_category) 

        # Effect category text
        if self.label:
            if self._debug_slot_names:
                self.label.text = self._slot_info.get_name() + ": " + self._categories.get_effect_category_name(self._effect_category) 
            else:
                self.label.text = self._categories.get_effect_category_name(self._effect_category) 
    
        super().update_displays()

    # Update switch brightness
    def set_switch_color(self, color):
        if self._effect_category == self._categories.get_category_not_assigned():
            # Set pixels to black (this effectively deactivates the LEDs) 
            color = Colors.BLACK

        super().set_switch_color(color)
    
    # Update label color, if any
    def set_label_color(self, color):
        if not self.label:
            return
        
        if self._effect_category == self._categories.get_category_not_assigned():
            # Do not dim the color when not assigned (this makes it black effectively) 
            self.label.back_color = color
        else:
            super().set_label_color(color)

    # Called by the Client class when a parameter request has been answered
    def parameter_changed(self, mapping):
        super().parameter_changed(mapping)

        if mapping != self._mapping_fxtype:
            return
        
        # Convert to effect category
        category = self._categories.get_effect_category(mapping.value)

        if self.debug:  # pragma: no cover
            self.print(" -> Receiving effect category " + repr(category))

        if category == self._effect_category:
            # Request status also when category has not changed
            super().do_update()
            return

        # New effect category
        self._effect_category = category

        if self._effect_category == self._categories.get_category_not_assigned():
            self.state = False

        self.update_displays()

        # Request status, too
        super().do_update()

    # Called when the client is offline (requests took too long)
    def request_terminated(self, mapping):
        super().request_terminated(mapping)
         
        if mapping != self._mapping_fxtype:
            return
        
        if self.debug:  # pragma: no cover
            self.print(" -> Terminated request for effect type, is the device offline?")
        
        self._effect_category = self._categories.get_category_not_assigned() 
        
        self.update_displays()

    # Reset the action
    def reset(self):
        super().reset()

        self._effect_category = self._categories.get_category_not_assigned() 
        self.update_displays()

    # Must reset all action states so the instance is being updated
    def force_update(self):
        super().force_update()
        
        self._current_category = -1


#######################################################################################################


# Category provider base class. A category provider must translate the value of 
# the effect type mapping set on the action's config to an effect category including
# the corresponding color and name.
#class EffectCategoryProvider:
#    # Must return the effect category for a mapping value
#    def get_effect_category(self, value):
#        raise Exception("Implement in child classes")
#    
#    # Must return the effect color for a mapping value
#    def get_effect_category_color(self, value):
#        return Colors.BLACK
#    
#    # Must return the effect name for a mapping value
#    def get_effect_category_name(self, value):
#        return ""
#    
#    # Must return the value interpreted as "not assigned"
#    def get_category_not_assigned(self):
#        raise Exception("Implement in child classes")
    

#######################################################################################################
 
 
## Provider class for slot information
#class SlotInfoProvider:
#    # Must return the slot name
#    def get_name(self):
#        raise Exception("Implement in child classes")

################################################################################################################################


# Simple action that prints a fixed text on the console
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
                
        self._reset_switches = Tools.get_option(config, "resetSwitches")
        self._ignore_own_switch = Tools.get_option(config, "ignoreOwnSwitch")
        self._reset_display_areas = Tools.get_option(config, "resetDisplayAreas")

    def push(self):
        if self._reset_switches:
            if self._ignore_own_switch:
                self.appl.reset_switches([self.switch])
            else:
                self.appl.reset_switches()

        if self._reset_display_areas:
            self.appl.reset_display_areas()

