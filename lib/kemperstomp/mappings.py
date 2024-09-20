#################################################################################################################################
# 
# Defines some useful MIDI mappings.
#
#################################################################################################################################
 
from adafruit_midi.control_change import ControlChange

from .src.model.KemperNRPNMessage import KemperNRPNMessage
from .src.model.KemperParameterMapping import KemperParameterMapping
from .definitions import KemperMidi

#################################################################################################################################

# Defines some useful MIDI mappings
class KemperMappings:

    # Effect slot enable/disable
    @staticmethod
    def EFFECT_SLOT_ON_OFF(slot_id):
        return KemperParameterMapping(
            set = ControlChange(
                KemperMidi.CC_EFFECT_SLOT_ENABLE[slot_id], 
                0    # Dummy value, will be overridden
            ),
            request = KemperNRPNMessage(               
                KemperMidi.NRPN_FUNCTION_REQUEST_SINGLE_PARAMETER, 
                KemperMidi.NRPN_SLOT_ADDRESS_PAGE[slot_id],
                KemperMidi.NRPN_EFFECT_PARAMETER_ADDRESS_ON_OFF
            ),
            response = KemperNRPNMessage(
                KemperMidi.NRPN_FUNCTION_RESPONSE_SINGLE_PARAMETER,
                KemperMidi.NRPN_SLOT_ADDRESS_PAGE[slot_id],
                KemperMidi.NRPN_EFFECT_PARAMETER_ADDRESS_ON_OFF
            )
        )
    
    # Effect slot type (request only)
    @staticmethod
    def EFFECT_SLOT_TYPE(slot_id):
        return KemperParameterMapping(
            request = KemperNRPNMessage(               
                KemperMidi.NRPN_FUNCTION_REQUEST_SINGLE_PARAMETER, 
                KemperMidi.NRPN_SLOT_ADDRESS_PAGE[slot_id],
                KemperMidi.NRPN_EFFECT_PARAMETER_ADDRESS_TYPE
            ),
            response = KemperNRPNMessage(               
                KemperMidi.NRPN_FUNCTION_RESPONSE_SINGLE_PARAMETER, 
                KemperMidi.NRPN_SLOT_ADDRESS_PAGE[slot_id],
                KemperMidi.NRPN_EFFECT_PARAMETER_ADDRESS_TYPE
            )
        )

    # Rig name (request only)
    RIG_NAME = KemperParameterMapping(
        request = KemperNRPNMessage(               
            KemperMidi.NRPN_FUNCTION_REQUEST_STRING_PARAMETER, 
            KemperMidi.NRPN_ADDRESS_PAGE_STRINGS,
            KemperMidi.NRPN_STRING_PARAMETER_ID_RIG_NAME
        ),
        response = KemperNRPNMessage(
            KemperMidi.NRPN_FUNCTION_RESPONSE_STRING_PARAMETER, 
            KemperMidi.NRPN_ADDRESS_PAGE_STRINGS,
            KemperMidi.NRPN_STRING_PARAMETER_ID_RIG_NAME
        ),
        type = KemperMidi.NRPN_PARAMETER_TYPE_STRING
    )

    # Rig date (request only)
    RIG_DATE = KemperParameterMapping(
        request = KemperNRPNMessage(               
            KemperMidi.NRPN_FUNCTION_REQUEST_STRING_PARAMETER, 
            KemperMidi.NRPN_ADDRESS_PAGE_STRINGS,
            KemperMidi.NRPN_STRING_PARAMETER_ID_RIG_DATE
        ),
        response = KemperNRPNMessage(
            KemperMidi.NRPN_FUNCTION_RESPONSE_STRING_PARAMETER, 
            KemperMidi.NRPN_ADDRESS_PAGE_STRINGS,
            KemperMidi.NRPN_STRING_PARAMETER_ID_RIG_DATE
        ),
        type = KemperMidi.NRPN_PARAMETER_TYPE_STRING
    )

    # Switch tuner mode on/off (no receive possible!)
    TUNER_MODE_ON_OFF = KemperParameterMapping(
        set = ControlChange(
            KemperMidi.CC_TUNER_MODE, 
            0    # Dummy value, will be overridden
        ),
    )

    # Rig volume
    RIG_VOLUME = KemperParameterMapping(
        set = KemperNRPNMessage(
            KemperMidi.NRPN_FUNCTION_SET_SINGLE_PARAMETER, 
            KemperMidi.NRPN_ADDRESS_PAGE_RIG_PARAMETERS,
            KemperMidi.NRPN_RIG_PARAMETER_VOLUME
        ),
        request = KemperNRPNMessage(
            KemperMidi.NRPN_FUNCTION_REQUEST_SINGLE_PARAMETER,
            KemperMidi.NRPN_ADDRESS_PAGE_RIG_PARAMETERS,
            KemperMidi.NRPN_RIG_PARAMETER_VOLUME
        ),
        response = KemperNRPNMessage(
            KemperMidi.NRPN_FUNCTION_RESPONSE_SINGLE_PARAMETER,
            KemperMidi.NRPN_ADDRESS_PAGE_RIG_PARAMETERS,
            KemperMidi.NRPN_RIG_PARAMETER_VOLUME
        ),
    )
