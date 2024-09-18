from .base.PushButtonAction import PushButtonAction
from ...Tools import Tools
from ....definitions import KemperMidi, Colors
from ....config import Config


# Implements bipolar parameters on base of the PushButtonAction class
class BinaryParameterAction(PushButtonAction):
    
    def __init__(self, appl, switch, config):
        super().__init__(appl, switch, config)

        self._mapping = self.config["mapping"]
        self._color = Tools.get_option(self.config, "color", Colors.DEFAULT_SWITCH_COLOR)
        self._value_on = Tools.get_option(self.config, "valueEnabled", KemperMidi.NRPN_PARAMETER_ON)
        self._value_off = Tools.get_option(self.config, "valueDisabled", KemperMidi.NRPN_PARAMETER_OFF)
        
        self._brightness_not_assigned = Config["ledBrightness"]["notAssigned"]
        self._brightness_on = Config["ledBrightness"]["on"]
        self._brightness_off = Config["ledBrightness"]["off"]

        self._current_display_status = -1
        self.update_displays()

    # Set state (called by base class)
    def set(self, enabled):
        if self._mapping.can_set == False:
            raise Exception("Binary parameter cannot be set")
        
        if enabled == True:
            self.appl.kemper.set(self._mapping, self._value_on)
        else:
            self.appl.kemper.set(self._mapping, self._value_off)

        self.appl.kemper.request(self._mapping)
        self.update_displays()

    # Request real state from controlled device
    def update(self):
        if self._mapping.can_receive == False:
            return            
        
        self.appl.kemper.request(self._mapping)

    # Update display and LEDs to the current state
    def update_displays(self):
        # Only update when type of state have been changed
        if self._current_display_status == self.state:
            return
        
        self._current_display_status = self.state

        # Switch LED color 
        self.switch.color = self.get_color() 

        if self.state == True:
            # Switched on
            self.switch.brightness = self._brightness_on
        else:
            # Switched off
            self.switch.brightness = self._brightness_off

    # Returns the color of the switch
    def get_color(self):
        return self._color

    # Receive MIDI messages
    def process(self, midi_message):
        if self._mapping.can_receive == False:
            return
                        
        status = self.appl.kemper.parse(self._mapping, midi_message)
        if status != None:
            self._receive_status(status)

    # Receive a status value (instance of KemperResponse)
    def _receive_status(self, response):
        self.print(" -> Receiving binary switch status " + repr(response.value))

        self.feedback_state(response.value)
        self.update_displays()
