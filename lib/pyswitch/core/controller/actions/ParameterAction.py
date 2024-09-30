from .base.PushButtonAction import PushButtonAction
from ...client.ClientRequest import ClientRequestListener
from ...client.ClientParameterMapping import ClientParameterMapping
from ...misc.Tools import Tools
from ....definitions import Colors
from ....defaults import FootSwitchDefaults, DisplayDefaults

# Implements bipolar parameters on base of the PushButtonAction class
class ParameterAction(PushButtonAction, ClientRequestListener):

    # config:
    # {
    #     "mapping":        A ClientParameterMapping instance. Can also be an array of mappings (only the first 
    #                       will be used to request values).
    #     "mappingDisable": A ClientParameterMapping instance only used for setting the "off" 
    #                       value. No requesting is used from that mapping. Optional. 
    #                       Can also be an array of mappings.
    #     "valueEnabled":   Value to set when enabled. Must be an array of values if mapping is an array.
    #     "valueDisabled":  Value to set when disabled. Must be an array of values if mappingDisable is an array.
    #}
    def __init__(self, appl, switch, config):
        super().__init__(appl, switch, config)

        self.uses_switch_leds = True

        # Action config
        self.color = Tools.get_option(self.config, "color", Colors.DEFAULT_SWITCH_COLOR)
        
        self._mapping = self.config["mapping"]                                                          # Can be an array
        self._mapping_off = Tools.get_option(self.config, "mappingDisable", None)                       # Can be an array
        self._value_on = Tools.get_option(self.config, "valueEnabled", 1)                               # Can be an array
        self._value_off = Tools.get_option(self.config, "valueDisabled", 0)                             # Can be an array
        
        self._text = Tools.get_option(self.config, "text", False)
        self._text_disabled = Tools.get_option(self.config, "textDisabled", False)

        self._get_request_mapping()        

        # Global config
        self._dim_factor_on = Tools.get_option(
            self.config, "displayDimFactorOn", 
            Tools.get_option(
                self.appl.config, 
                "displayDimFactorOn", 
                DisplayDefaults.DEFAULT_SLOT_DIM_FACTOR_ON
            )
        )
        self._dim_factor_off = Tools.get_option(
            self.config, "displayDimFactorOff", 
            Tools.get_option(
                self.appl.config, 
                "displayDimFactorOff", 
                DisplayDefaults.DEFAULT_SLOT_DIM_FACTOR_OFF
            )
        )

        if Tools.get_option(self.config, "ledBrightness") != False:
            self._brightness_on = Tools.get_option(self.config["ledBrightness"], "on", FootSwitchDefaults.DEFAULT_BRIGHTNESS_ON)
            self._brightness_off = Tools.get_option(self.config["ledBrightness"], "off", FootSwitchDefaults.DEFAULT_BRIGHTNESS_OFF)
        elif Tools.get_option(self.appl.config, "ledBrightness") != False:
            self._brightness_on = Tools.get_option(self.appl.config["ledBrightness"], "on", FootSwitchDefaults.DEFAULT_BRIGHTNESS_ON)
            self._brightness_off = Tools.get_option(self.appl.config["ledBrightness"], "off", FootSwitchDefaults.DEFAULT_BRIGHTNESS_OFF)
        else:
            self._brightness_on = FootSwitchDefaults.DEFAULT_BRIGHTNESS_ON
            self._brightness_off = FootSwitchDefaults.DEFAULT_BRIGHTNESS_OFF

        self._current_display_status = -1
        self._current_color = -1

    # Set state (called by base class)
    def set(self, enabled):        
        # Get mappings to execute
        mapping_definitions = self._get_set_mappings(enabled)

        for mapping_def in mapping_definitions:
            self.appl.client.set(mapping_def["mapping"], mapping_def["value"])

        # Request value
        self._request_value()

    # Request real state from controlled device
    def update(self):
        self._request_value()

    # Cancel eventually pending requests (which might return outdated values)
    # Request parameter value
    def _request_value(self):
        if self._request_mapping == None:
            return            
        
        if self.debug == True:
            self.print("Request value")

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
        if self.label == None:
            return
            
        if self.state == True:
            self.label.back_color = self._dim_color(color, self._dim_factor_on)
        else:
            self.label.back_color = self._dim_color(color, self._dim_factor_off)

    # Update text if set
    def _update_label_text(self):
        if self.label == None:
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
        if isinstance(candidates, ClientParameterMapping):
            all = [candidates]

            if state == True:
                values = [self._value_on]
            else:
                values = [self._value_off]
        else:
            all = candidates

            if state == True:
                values = self._value_on
            else:
                values = self._value_off

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
            if self._mapping.can_receive == True:
                self._request_mapping_value_on = self._value_on
                self._request_mapping = self._mapping
        else:
            # Array of mappings: Use the first one capable of receiving values
            for i in range(len(self._mapping)):
                mapping = self._mapping[i]

                if mapping.can_receive == True:
                    self._request_mapping = mapping
                    self._request_mapping_value_on = self._value_on[i]
                    break

    # Must reset all action states so the instance is being updated
    def force_update(self):
        self._current_display_status = -1
        self._current_color = -1

    # Must reset the displays
    def reset_display(self):
        if self.label != None:
            self.label.text = ""
            self.label.back_color = Colors.DEFAULT_LABEL_COLOR

        self.switch_color = Colors.BLACK
        self.switch_brightness = 0

    # Called by the Client class when a parameter request has been answered
    def parameter_changed(self, mapping):
        if not self.enabled:
            return
         
        if self._request_mapping == None:
            return            
        
        if mapping != self._request_mapping:
            return
        
        state = False
        if mapping.value >= self._request_mapping_value_on:
            state = True

        if self.debug == True:
            self.print(" -> Receiving binary switch status " + repr(mapping.value) + ", counted as " + repr(state))

        self.feedback_state(state)

    # Called when the client is offline (requests took too long)
    def request_terminated(self, mapping):
        if self._request_mapping == None:
            return        
        
        if mapping != self._request_mapping:
            return
        
        if self.debug == True:
            self.print(" -> Terminated request for parameter value, is the device offline?")
        
        self.state = False

        self.update_displays()

