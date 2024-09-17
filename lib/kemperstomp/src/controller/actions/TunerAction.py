from .Action import Action
from ...model.Kemper import Kemper
from ...Tools import Tools
from ....config import Config
from ....definitions import KemperDefinitions


# Implements the effect enable/disable footswitch action
class TunerAction(Action):
    
    # Switch states
    STATE_ON = "on"
    STATE_OFF = "off"
    STATE_UNKNOWN = "unknown"

    def __init__(self, appl, switch, config):
        super().__init__(appl, switch, config)

        self._mode = self.config["mode"]
        self._state = TunerAction.STATE_UNKNOWN

        self._brightness_not_assigned = Config["ledBrightness"]["notAssigned"]
        self._brightness_on = Config["ledBrightness"]["on"]
        self._brightness_off = Config["ledBrightness"]["off"]

        self.label.text = KemperDefinitions.TUNER_MODE_NAME
        self.switch.color = Tools.dim_color(KemperDefinitions.TUNER_MODE_COLOR)
        self.switch.brightness = self._brightness_off

    # Process the action
    def trigger(self, event):
        self._toggle()  # TODO modes!
        self._update()

        self.appl.kemper.set_tuner_mode(self._enabled())

        # Request status of the effect to update the LEDs
        #self.appl.kemper.request_tuner_mode()

    # Request effect type (which will trigger a status request)
    #def update(self):
        #self.appl.kemper.request_tuner_mode()

    # Receive MIDI messages
    #def process(self, midi_message):
    #    # Receive MIDI messages related to this action, only if a MIDI message has been received
    #    if midi_message == None:
    #        return
    #   
    #    response = self.appl.kemper.parse_tuner_mode(midi_message)
    #    if response != None:
    #        self._receive_mode(response)

    # Receive a type value (instance of KemperResponse)
    #def _receive_mode(self, response):
    #    self.print(" -> Receiving tuner mode: " + repr(response.value))
    #
    #    if response.value == True:
    #        if self._state != TunerAction.STATE_ON:
    #            self._state = TunerAction.STATE_ON
    #            self.switch.brightness = self._brightness_on
    #
    #            if self.label != None:
    #                self.label.back_color = KemperDefinitions.TUNER_MODE_COLOR

    #    else:
    #        if self._state != TunerAction.STATE_OFF:
    #            self._state = TunerAction.STATE_OFF
    #            self.switch.brightness = self._brightness_off

    #            if self.label != None:
    #                self.label.back_color = Tools.dim_color(KemperDefinitions.TUNER_MODE_COLOR)

    # Toggle status
    def _toggle(self):
        if self._enabled() == True:
            self._state = TunerAction.STATE_OFF
        else:
            self._state = TunerAction.STATE_ON
        
    # Update display and switch
    def _update(self):
        if self._enabled() == True:            
            self.switch.brightness = self._brightness_on
            
            if self.label != None:
                self.label.back_color = KemperDefinitions.TUNER_MODE_COLOR

        else:
            self.switch.brightness = self._brightness_off
            if self.label != None:
                self.label.back_color = Tools.dim_color(KemperDefinitions.TUNER_MODE_COLOR)
    
    # Returns if the effect is currently enabled
    def _enabled(self):
        return self._state == TunerAction.STATE_ON

