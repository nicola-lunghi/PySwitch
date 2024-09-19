from .base.PushButtonAction import PushButtonAction
from ...model.KemperRequest import KemperRequestListener
from ...Tools import Tools
from ....definitions import KemperMidi, Colors
from ....config import Config


# Implements bipolar parameters on base of the PushButtonAction class
class BinaryParameterAction(PushButtonAction, KemperRequestListener):
    
    def __init__(self, appl, switch, config, index):
        super().__init__(appl, switch, config, index)

        self.color = Tools.get_option(self.config, "color", Colors.DEFAULT_SWITCH_COLOR)

        self._mapping = self.config["mapping"]
        self._value_on = Tools.get_option(self.config, "valueEnabled", KemperMidi.NRPN_PARAMETER_ON)
        self._value_off = Tools.get_option(self.config, "valueDisabled", KemperMidi.NRPN_PARAMETER_OFF)
        
        self._brightness_not_assigned = Config["ledBrightness"]["notAssigned"]
        self._brightness_on = Config["ledBrightness"]["on"]
        self._brightness_off = Config["ledBrightness"]["off"]

        self._current_display_status = -1
        self._current_color = -1

    # Set state (called by base class)
    def set(self, enabled):
        if self._mapping.can_set == False:
            raise Exception("Binary parameter cannot be set")
        
        if enabled == True:
            self.appl.kemper.set(self._mapping, self._value_on)
        else:
            self.appl.kemper.set(self._mapping, self._value_off)

        self.request_value()

        self.update_displays()

    # Request real state from controlled device
    def update(self):
        self.request_value()

    # Request parameter value
    def request_value(self):
        self.print("Request value")
        if self._mapping.can_receive == False:
            return            
        
        self.appl.kemper.request(self._mapping, self)

    # Update display and LEDs to the current state
    def update_displays(self):
        # Set color, if new
        if self.color != self._current_color:
            self._current_color = self.color
        
            self.set_switch_color(self.color)
            self.set_label_color(self.color)
    
        # Only update when state have been changed
        if self._current_display_status != self.state:
            self._current_display_status = self.state

            self.set_switch_color(self.color)
            self.set_label_color(self.color)

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
            self.label.back_color = color
        else:
            self.label.back_color = Tools.dim_color(color)

    # Called by the Kemper class when a parameter request has been answered
    def parameter_changed(self, mapping):
        if mapping != self._mapping:
            return
        
        self.print(" -> Receiving binary switch status " + repr(mapping.value))

        self.feedback_state(mapping.value)
        
        self.update_displays()

    # Called when the Kemper is offline (requests took too long)
    def request_terminated(self, mapping):
        if mapping != self._mapping:
            return
        
        self.print(" -> Terminated request for parameter value, is the device offline?")
        self.state = False

        self.update_displays()

