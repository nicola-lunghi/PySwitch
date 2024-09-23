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
            name = "Effect Status " + str(slot_id),
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
            name = "Effect Type " + str(slot_id),
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

    # Freeze for slot
    @staticmethod
    def FREEZE(slot_id):
        return KemperParameterMapping(
            name = "Freeze " + str(slot_id),
            set = KemperNRPNMessage(
                KemperMidi.NRPN_FUNCTION_SET_SINGLE_PARAMETER, 
                KemperMidi.NRPN_ADDRESS_PAGE_FREEZE,
                KemperMidi.NRPN_FREEZE_SLOT_PARAMETER_ADDRESSES[slot_id]
            ),
            request = KemperNRPNMessage(               
                KemperMidi.NRPN_FUNCTION_REQUEST_SINGLE_PARAMETER, 
                KemperMidi.NRPN_ADDRESS_PAGE_FREEZE,
                KemperMidi.NRPN_FREEZE_SLOT_PARAMETER_ADDRESSES[slot_id]
            ),
            response = KemperNRPNMessage(               
                KemperMidi.NRPN_FUNCTION_RESPONSE_SINGLE_PARAMETER, 
                KemperMidi.NRPN_ADDRESS_PAGE_FREEZE,
                KemperMidi.NRPN_FREEZE_SLOT_PARAMETER_ADDRESSES[slot_id]
            )
        )

    # Rig name (request only)
    RIG_NAME = KemperParameterMapping(
        name = "Rig Name",
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
        name = "Rig Date",
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
        name = "Tuner Mode",
        set = ControlChange(
            KemperMidi.CC_TUNER_MODE, 
            0    # Dummy value, will be overridden
        ),
    )

    # Rig volume
    RIG_VOLUME = KemperParameterMapping(
        name = "Rig Volume",
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

    # Amp name (request only)
    AMP_NAME = KemperParameterMapping(
        name = "Amp Name",
        request = KemperNRPNMessage(               
            KemperMidi.NRPN_FUNCTION_REQUEST_STRING_PARAMETER, 
            KemperMidi.NRPN_ADDRESS_PAGE_STRINGS,
            KemperMidi.NRPN_STRING_PARAMETER_ID_AMP_NAME
        ),
        response = KemperNRPNMessage(
            KemperMidi.NRPN_FUNCTION_RESPONSE_STRING_PARAMETER, 
            KemperMidi.NRPN_ADDRESS_PAGE_STRINGS,
            KemperMidi.NRPN_STRING_PARAMETER_ID_AMP_NAME
        ),
        type = KemperMidi.NRPN_PARAMETER_TYPE_STRING
    )

    # Amp name (request only)
    CABINET_NAME = KemperParameterMapping(
        name = "Cab Name",
        request = KemperNRPNMessage(               
            KemperMidi.NRPN_FUNCTION_REQUEST_STRING_PARAMETER, 
            KemperMidi.NRPN_ADDRESS_PAGE_STRINGS,
            KemperMidi.NRPN_STRING_PARAMETER_ID_CABINET_NAME
        ),
        response = KemperNRPNMessage(
            KemperMidi.NRPN_FUNCTION_RESPONSE_STRING_PARAMETER, 
            KemperMidi.NRPN_ADDRESS_PAGE_STRINGS,
            KemperMidi.NRPN_STRING_PARAMETER_ID_CABINET_NAME
        ),
        type = KemperMidi.NRPN_PARAMETER_TYPE_STRING
    )
    
    NEXT_BANK = KemperParameterMapping(
        name = "Next Bank",
        set = ControlChange(
            KemperMidi.CC_BANK_INCREASE,
            0    # Dummy value, will be overridden
        )
    )

    PREVIOUS_BANK = KemperParameterMapping(
        name = "Prev Bank",
        set = ControlChange(
            KemperMidi.CC_BANK_DECREASE,
            0    # Dummy value, will be overridden
        )
    )