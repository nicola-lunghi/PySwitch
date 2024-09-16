
from .Action import Action
from ..model.KemperProfilerPlayer import KemperProfilerPlayer

from ...kemperstomp_config import Config

# Implements the effect enable/disable footswitch action
class EffectEnableAction(Action):
    
    # Switch states
    STATE_ON = "on"
    STATE_OFF = "off"
    STATE_NOT_ASSIGNED = "na"

    def __init__(self, appl, switch, config):
        super().__init__(appl, switch, config)

        self.slot_id = self.config["slot"]
        self.effect_type = -1
        self.state = EffectEnableAction.STATE_OFF

        self.brightness_not_assigned = Config["ledBrightness"]["notAssigned"]
        self.brightness_on = Config["ledBrightness"]["on"]
        self.brightness_off = Config["ledBrightness"]["off"]

    # Process the action
    def down(self):
        # Enable/disable effect slot
        self.appl.kemper.set_slot_enabled(self.slot_id, self._enabled())

        # Request status of the effect to update the LEDs
        self.appl.kemper.request_effect_status(self.slot_id)

    # Receive MIDI messages
    def receive(self, midi_message):
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
        if response.value == self.effect_type:
            return

        self.effect_type = response.value

        # Set UI background color according to effect type
        self.switch.set_color(KemperProfilerPlayer.TYPE_COLORS[self.effect_type])

        # Set effect name on UI
        self.appl.ui.effect_slots[self.slot_id].set_text(KemperProfilerPlayer.TYPE_NAMES[self.effect_type])

        if self.effect_type == KemperProfilerPlayer.TYPE_NONE:
            # No effect assigned: Switch off lights
            self.switch.set_brightness(self.brightness_not_assigned)

        # Request status of the effect after type changes
        self.appl.kemper.request_effect_status(self.slot_id)

    # Receive a status value (instance of KemperResponse)
    def _receive_status(self, response):
        if response.value == True:
            self.state = EffectEnableAction.STATE_ON
            self.switch.set_brightness(self.brightness_on)
        else:
            self.state = EffectEnableAction.STATE_OFF
            self.switch.set_brightness(self.brightness_off)

    # Returns if the effect is currently enabled
    def _enabled(self):
        return self.state == EffectEnableAction.STATE_ON

