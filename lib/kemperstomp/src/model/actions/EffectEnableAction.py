from .Action import Action
from ..Kemper import Kemper
from ....config import Config


# Implements the effect enable/disable footswitch action
class EffectEnableAction(Action):
    
    # Switch states
    STATE_ON = "on"
    STATE_OFF = "off"
    STATE_NOT_ASSIGNED = "na"

    def __init__(self, appl, switch, config):
        super().__init__(appl, switch, config)

        self.slot_id = self.config["slot"]              # Kemper effect slot
        self._effect_type = -1
        self._state = EffectEnableAction.STATE_OFF

        self._brightness_not_assigned = Config["ledBrightness"]["notAssigned"]
        self._brightness_on = Config["ledBrightness"]["on"]
        self._brightness_off = Config["ledBrightness"]["off"]

    # Process the action
    def trigger(self, event):
        # Enable/disable effect slot
        self.appl.kemper.set_slot_enabled(self.slot_id, not self._enabled())

        # Request status of the effect to update the LEDs
        self.appl.kemper.request_effect_status(self.slot_id)

    # Request effect type (which will trigger a status request)
    def update(self):
        self.appl.kemper.request_effect_type(self.slot_id)

    # Receive MIDI messages
    def process(self, midi_message):
        # Receive MIDI messages related to this action, only if a MIDI message has been received
        if midi_message == None:
            return
        
        # Effect type
        type = self.appl.kemper.parse_effect_type(midi_message, self.slot_id)
        if type != None:
            self._receive_type(type)

        # Effect status
        status = self.appl.kemper.parse_effect_status(midi_message, self.slot_id)
        if status != None:
            self._receive_status(status)

    # Receive a type value (instance of KemperResponse)
    def _receive_type(self, response):
        self.print(" -> Receiving effect type " + repr(response.value))

        if response.value == self._effect_type:
            # Request status also when type has not changed
            self.appl.kemper.request_effect_status(self.slot_id)

            return

        self._effect_type = response.value

        # Set UI background color according to effect type
        self.switch.color = Kemper.TYPE_COLORS[self._effect_type]

        # Set effect name on UI, if a label is assigned
        if self.label != None:
            self.label.text = Kemper.TYPE_NAMES[self._effect_type]            

        if self._effect_type == Kemper.TYPE_NONE:
            # No effect assigned: Switch off lights
            self.switch.brightness = self._brightness_not_assigned

        # Request status of the effect after type changes
        self.appl.kemper.request_effect_status(self.slot_id)

    # Receive a status value (instance of KemperResponse)
    def _receive_status(self, response):
        self.print(" -> Receiving effect status " + repr(response.value))

        if response.value == True:
            self._state = EffectEnableAction.STATE_ON
            self.switch.brightness = self._brightness_on
        else:
            self._state = EffectEnableAction.STATE_OFF
            self.switch.brightness = self._brightness_off

    # Returns if the effect is currently enabled
    def _enabled(self):
        return self._state == EffectEnableAction.STATE_ON

