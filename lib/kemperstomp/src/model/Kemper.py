from adafruit_midi.control_change import ControlChange
from adafruit_midi.system_exclusive import SystemExclusive

from .KemperNRPNMessage import KemperNRPNMessage
from ..Tools import Tools
from...config import Config

# Implements all MIDI communication to and from the Kemper
class Kemper:

    def __init__(self, midi):
        self._midi = midi        
        
    # Sends the SET message of a mapping
    def set(self, mapping, value):
        if mapping.set == None:
            raise Exception("No SET message prepared for this MIDI mapping")
        
        if isinstance(mapping.set, ControlChange):
            # Set value
            mapping.set.value = value

        if isinstance(mapping.set, SystemExclusive):
            raise Exception("Setting Kemper parameters by SysEx is not implemented yet")

        if isinstance(mapping.set, KemperNRPNMessage):
            raise Exception("Setting Kemper parameters by NRPN is not implemented yet")
        
        self._print("Send SET message: " + repr(mapping.set))

        self._midi.send(mapping.set)

    # Send the request message of a mapping
    def request(self, mapping):
        if mapping.request == None:
            raise Exception("No REQUEST message prepared for this MIDI mapping")
        
        if isinstance(mapping.set, ControlChange):
            raise Exception("Parameter requests do not work with ControlChange. Use KemperNRPNMessage (or SystemExclusive) instead.")

        self._print("Send REQUEST message: " + repr(mapping.request))

        self._midi.send(mapping.request)

    # Parses an incoming MIDI message. If the message belongs to the mapping's request,
    # returns the received value. If not, returns None.
    def parse(self, mapping, midi_message):
        if not isinstance(midi_message, SystemExclusive):
            return None

        response = list(midi_message.data)
        self._print("Receive message: " + repr(response))
        
        if response[:-3] != [0x00, 0x00, 0x01, 0x00, Slots.SLOT_ADDRESS_PAGE[slot_id]]:
            # Message does not belong to this slot
            return None

        if response[5] != response_type:
            # Message is the wrong response type
            return None

        if response[5] == KemperDefinitions.RESPONSE_ID_EFFECT_TYPE:
            # Response to an effect type request
            kpp_effect_type = response[-2] * 128 + response[-1]
            
            return KemperResponse(
                KemperDefinitions.RESPONSE_ID_EFFECT_TYPE,
                self.get_effect_type(kpp_effect_type)
            )
        
        elif response[5] == KemperDefinitions.RESPONSE_ID_EFFECT_STATUS:
            # Response to an effect status request
            if (response[-1] == KemperDefinitions.RESPONSE_ANSWER_STATUS_ON):
                # Effect on
                return KemperResponse(
                    KemperDefinitions.RESPONSE_ID_EFFECT_TYPE,
                    True
                )
            elif (response[-1] == KemperDefinitions.RESPONSE_ANSWER_STATUS_OFF):
                # Effect off
                return KemperResponse(
                    KemperDefinitions.RESPONSE_ID_EFFECT_TYPE,
                    False
                )
            
    # Debug console output
    def _print(self, msg):
        if Tools.get_option(Config, "debugKemper") != True:
            return
        
        Tools.print("Kemper: " + msg)