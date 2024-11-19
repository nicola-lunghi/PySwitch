from micropython import const
from ...misc import DEFAULT_SWITCH_COLOR, Updateable, Colors, DEFAULT_LABEL_COLOR


class Callback(Updateable):
    def __init__(self):
        super().__init__()
        
        self._initialized = False

    # Can optionally return mappings which will be listened to.
    def get_mappings(self):
        return []
    
    # Must be called before usage
    def init(self, appl, listener):
        if self._initialized: 
            return
        
        self._appl = appl
        self._listener = listener

        for m in self.get_mappings():
            self._appl.client.register(m, self)

        self._appl.add_updateable(self)

        self._initialized = True

    def update(self):
        for m in self.get_mappings():
            self._appl.client.request(m, self)

    def parameter_changed(self, mapping):
        # Take over value before calling the listener
        for m in self.get_mappings():
            if m != mapping:
                continue

            m.value = mapping.value

        self._listener.parameter_changed(mapping)

    def request_terminated(self, mapping):
        # Clear value before calling the listener
        for m in self.get_mappings():
            if m != mapping:
                continue

            m.value = None

        self._listener.request_terminated(mapping)


###########################################################################################################


# Brightness values 
DEFAULT_LED_BRIGHTNESS_ON = 0.3
DEFAULT_LED_BRIGHTNESS_OFF = 0.02

# Dim factor for disabled effect slots (TFT display only)
DEFAULT_SLOT_DIM_FACTOR_ON = 1
DEFAULT_SLOT_DIM_FACTOR_OFF = 0.2

class BinaryParameterCallback(Callback):

    # Comparison modes (for the valueEnable value when requesting a value)
    EQUAL = const(0)                 # Enable when exactly the valueEnable value comes in
    
    GREATER = const(10)              # Enable when a value greater than valueEnable comes in
    GREATER_EQUAL = const(20)        # Enable when the valueEnable value comes in, or anything greater

    LESS = const(30)                 # Enable when a value less than valueEnable comes in
    LESS_EQUAL = const(40)           # Enable when the valueEnable value comes in, or anything less

    NO_STATE_CHANGE = const(999)     # Do not receive any values

    def __init__(self, 
                 
                 # A ClientParameterMapping instance. See mappings.py for some predeifined ones.
                 mapping, 

                 # Mapping to be used for disabling the functionality again (only used for sending)
                 mapping_disable = None,

                 # Color to be used
                 color = DEFAULT_SWITCH_COLOR,

                 # Text (optional)
                 text = None,

                 # Text for diabled state (optional)
                 text_disabled = None,

                 # Value to be sent as "enabled". Optional: Default is 1. If mapping.set is a list, this must
                 # also be a list of values for the set messages in the mapping.
                 value_enable = 1,                                       

                 # Value to be sent as "disabled". Optional: Default is 0. If mapping.set is a list, this must
                 # also be a list of values for the set messages in the mapping.
                 # SPECIAL: If you set this (or items of this) to "auto", the "disabled" value will be determined from the 
                 # client's current parameter value when the action state is False (the old value is restored).
                 value_disable = 0,                                      
                 
                 # Optional: The value of incoming messages will be compared against this to determine state
                 # (acc. to the comparison mode). If not set, "valueEnable" is used (first entry if valueEnabled is a list). 
                 reference_value = 1,

                 # Mode of comparison when receiving a value. Default is GREATER_EQUAL. 
                 comparison_mode = 20,

                 # Dim factor in range [0..1] for on state (display label) Optional.
                 display_dim_factor_on = DEFAULT_SLOT_DIM_FACTOR_ON,

                 # Dim factor in range [0..1] for off state (display label) Optional.
                 display_dim_factor_off = DEFAULT_SLOT_DIM_FACTOR_OFF,
                 
                 # LED brightness [0..1] for on state (Switch LEDs) Optional.
                 led_brightness_on = DEFAULT_LED_BRIGHTNESS_ON,

                 # LED brightness [0..1] for off state (Switch LEDs) Optional.
                 led_brightness_off = DEFAULT_LED_BRIGHTNESS_OFF
        ):
        super().__init__()

        self._mapping = mapping
        self._mapping_disable = mapping_disable

        self._value_enable = value_enable
        self._value_disable = value_disable
        self._reference_value = reference_value
        self._text = text
        self._text_disabled = text_disabled
        self._comparison_mode = comparison_mode
        self._display_dim_factor_on = display_dim_factor_on
        self._display_dim_factor_off = display_dim_factor_off
        self._led_brightness_on = led_brightness_on
        self._led_brightness_off = led_brightness_off
        self._color = color

        self._current_display_state = -1
        self._current_value = self       # Just some value which will never occur as a mapping value ;)
        self._current_color = -1

        # Auto mode for value_disable
        self._update_value_disabled = False
        if not isinstance(self._value_disable, list):
            self._update_value_disabled = (self._value_disable == "auto")
        else:
            self._update_value_disabled = [v == "auto" for v in self._value_disable]            

    def init(self, appl, listener):
        super().init(appl, listener)

        self._appl = appl

    def get_mappings(self):
        yield self._mapping  # Only listen to the main mapping (mapping_disable is just used for sending stuff)

    def state_changed_by_user(self, action):
        if action.state:
            set_mapping = self._mapping
            value = self._value_enable
        else:
            if self._mapping_disable:
                set_mapping = self._mapping_disable
            else:
                set_mapping = self._mapping

            value = self._value_disable

        if not isinstance(self._value_disable, list):
            if value != "auto":
                self.appl.client.set(set_mapping, value)
        else:
            auto_contained = False
            for v in self._value_disable:
                if v == "auto":
                    auto_contained = True
                    break
            if not auto_contained:
                self.appl.client.set(set_mapping, value)

        # Request value
        self.update()

    def update_displays(self, action):
        if self._mapping.value != self._current_value:
            self._current_value = self._mapping.value
            self.evaluate_value(action, self._mapping.value)

        # Set color, if new
        if self._color != self._current_color:
            self._current_color = self._color
        
            self.set_switch_color(action, self._color)
            self.set_label_color(action, self._color)
            self._update_label_text(action)            
    
        # Update when state have been changed
        if self._current_display_state != action.state:
            self._current_display_state = action.state

            self.set_switch_color(action, self._color)
            self.set_label_color(action, self._color)
            self._update_label_text(action)

    # Evaluate a new value
    def evaluate_value(self, action, value):
        state = False

        if value != None:
            if self._comparison_mode == self.EQUAL:
                if value == self._reference_value:
                    state = True

            elif self._comparison_mode == self.GREATER_EQUAL:
                if value >= self._reference_value:
                    state = True

            elif self._comparison_mode == self.GREATER:
                if value > self._reference_value: 
                    state = True

            elif self._comparison_mode == self.LESS_EQUAL:
                if value <= self._reference_value:
                    state = True

            elif self._comparison_mode == self.LESS:
                if value < self._reference_value: 
                    state = True        

            elif self._comparison_mode == self.NO_STATE_CHANGE:
                state = self.state

            else:
                raise Exception() #"Invalid comparison mode: " + repr(self._comparison_mode))        

        action.feedback_state(state)        

        # If enabled, remember the value for later when disabled
        if state == True or not self._update_value_disabled:
            return
        
        if not isinstance(self._value_disable, list):
            self._value_disable = value
        else:
            for i in range(len(self._value_disable)):
                if self._update_value_disabled[i]:
                    self._value_disable[i] = value

    # Update switch brightness
    def set_switch_color(self, action, color):
        # Update switch LED color 
        action.switch_color = color

        if action.state == True and self._mapping.response:
            # Switched on
            action.switch_brightness = self._led_brightness_on
        else:
            # Switched off
            action.switch_brightness = self._led_brightness_off

   # Update label color, if any
    def set_label_color(self, action, color):
        if not action.label:
            return
            
        if action.state == True and self._mapping.response:
            action.label.back_color = self._dim_color(color, self._display_dim_factor_on)
        else:
            action.label.back_color = self._dim_color(color, self._display_dim_factor_off)

    # Update text if set
    def _update_label_text(self, action):
        if not action.label:
            return
            
        if self._text == False:
            return
        
        if action.state == True or not self._mapping.response:
            action.label.text = self._text
        else:
            if self._text_disabled != False:
                action.label.text = self._text_disabled
            else:
                action.label.text = self._text

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