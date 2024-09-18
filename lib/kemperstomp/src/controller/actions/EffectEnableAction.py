from .base.PushButtonAction import PushButtonAction
from ...model.Kemper import Kemper
from ...Tools import Tools
from ....config import Config


# Implements the effect enable/disable footswitch action
class EffectEnableAction(PushButtonAction):
    
    def __init__(self, appl, switch, config):
        super().__init__(appl, switch, config)

        self._slot_id = self.config["slot"]              # Kemper effect slot ID
        self._effect_type = -1                           # Effect type (as defined in Kemper class)

        self._brightness_not_assigned = Config["ledBrightness"]["notAssigned"]
        self._brightness_on = Config["ledBrightness"]["on"]
        self._brightness_off = Config["ledBrightness"]["off"]

        self._current_display_type = -1
        self._current_display_status = False

        self.update_displays()

    # Set state (called by base class)
    def set(self, enabled):
        # Enable/disable effect slot
        self.appl.kemper.set_slot_enabled(self._slot_id, enabled)

        # Request status of the effect to update the LEDs
        self.appl.kemper.request_effect_status(self._slot_id)

        self.update_displays()

    # Request effect type periodically (which itself will trigger a status request)
    def update(self):
        self.appl.kemper.request_effect_type(self._slot_id)

    # Update display and LEDs to the current state and effect type
    def update_displays(self):
        # Only update when type of state have been changed
        if self._current_display_type == self._effect_type and self._current_display_status == self.state:
            return
        
        self._current_display_type = self._effect_type
        self._current_display_status = self.state

        # Effect type text
        if self.label != None:
            self.label.text = Kemper.TYPE_NAMES[self._effect_type]            

        # Switch LED color (this is dimmed by brightness and stays the same for all states)
        self.switch.color = Kemper.TYPE_COLORS[self._effect_type]

        if self._effect_type == Kemper.TYPE_NONE:            
            # No effect assigned
            self.switch.brightness = self._brightness_not_assigned

            if self.label != None:
                self.label.back_color = Tools.dim_color(Kemper.TYPE_COLORS[self._effect_type])

        elif self.state == True:
            # Switched on
            self.switch.brightness = self._brightness_on

            if self.label != None:
                self.label.back_color = Kemper.TYPE_COLORS[self._effect_type]

        else:
            # Switched off
            self.switch.brightness = self._brightness_off

            if self.label != None:
                self.label.back_color = Tools.dim_color(Kemper.TYPE_COLORS[self._effect_type])

    # Receive MIDI messages
    def process(self, midi_message):
        # Receive MIDI messages related to this action, only if a MIDI message has been received
        if midi_message == None:
            return
        
        # Effect type
        type = self.appl.kemper.parse_effect_type(midi_message, self._slot_id)
        if type != None:
            self._receive_type(type)

        # Effect status
        status = self.appl.kemper.parse_effect_status(midi_message, self._slot_id)
        if status != None:
            self._receive_status(status)

    # Receive a type value (instance of KemperResponse)
    def _receive_type(self, response):
        self.print(" -> Receiving effect type " + repr(response.value))

        if response.value == self._effect_type:
            # Request status also when type has not changed
            self._request_status()
            return

        # New effect type
        self._effect_type = response.value

        self.update_displays()
        self._request_status()

    # Request status of the effect 
    def _request_status(self):
        if self._effect_type == Kemper.TYPE_NONE:
            return
                
        self.appl.kemper.request_effect_status(self._slot_id)

    # Receive a status value (instance of KemperResponse)
    def _receive_status(self, response):
        self.print(" -> Receiving effect status " + repr(response.value))

        self.feedback_state(response.value)
        self.update_displays()
