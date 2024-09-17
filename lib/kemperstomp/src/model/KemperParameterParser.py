from adafruit_midi.system_exclusive import SystemExclusive

from .KemperResponse import KemperResponse
from ...definitions import KemperDefinitions, Slots


# Implements parsing of Kemper parameter responses
class KemperParameterParser:

    # Parse a response for the current rig name
    def parse_rig_name(self, midi_message):
        return self.parse_global_parameter(midi_message, KemperDefinitions.RESPONSE_PREFIX_RIG_NAME)
        
    # Parse a response for the current rig last changed date
    def parse_rig_date(self, midi_message):
        return self.parse_global_parameter(midi_message, KemperDefinitions.RESPONSE_PREFIX_RIG_DATE)

    # Parse a global parameter response
    def parse_global_parameter(self, midi_message, response_prefix):
        if not isinstance(midi_message, SystemExclusive):
            return None

        response = list(midi_message.data)
                
        if response[:6] != response_prefix:
            return None
        
        return KemperResponse(
            KemperDefinitions.RESPONSE_ID_GLOBAL_PARAMETER,
            ''.join(chr(int(c)) for c in response[6:-1])
        )

    # Parse a response for an effect type. Returns None if not relevant to the context.
    def parse_effect_type(self, midi_message, slot_id):
        return self.parse_effect_response(midi_message, slot_id, KemperDefinitions.RESPONSE_ID_EFFECT_TYPE)

    # Parse a response for an effect status. Returns None if not relevant to the context.
    def parse_effect_status(self, midi_message, slot_id):
        return self.parse_effect_response(midi_message, slot_id, KemperDefinitions.RESPONSE_ID_EFFECT_STATUS)

    # Parse a response for an effect parameter. Returns None if not relevant to the context.
    def parse_effect_response(self, midi_message, slot_id, response_type):
        if not isinstance(midi_message, SystemExclusive):
            return None

        response = list(midi_message.data)
                
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
            