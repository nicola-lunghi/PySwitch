from micropython import const
from .. import KemperNRPNMessage
from ....controller.Client import ClientParameterMapping
from .. import NRPN_FUNCTION_REQUEST_STRING_PARAMETER, NRPN_FUNCTION_RESPONSE_STRING_PARAMETER, NRPN_FUNCTION_SET_SINGLE_PARAMETER, NRPN_FUNCTION_RESPONSE_SINGLE_PARAMETER, NRPN_FUNCTION_REQUEST_SINGLE_PARAMETER, NRPN_ADDRESS_PAGE_STRINGS

_NRPN_ADDRESS_PAGE_RIG_PARAMETERS = const(0x04)

_NRPN_RIG_PARAMETER_VOLUME = const(0x01)
_NRPN_STRING_PARAMETER_ID_RIG_COMMENT = const(0x04)
_NRPN_STRING_PARAMETER_ID_RIG_DATE = const(0x03)


# Rig comment (request only)
def MAPPING_RIG_COMMENT(): 
    return ClientParameterMapping(
        name = "Rig Comment",
        request = KemperNRPNMessage(               
            NRPN_FUNCTION_REQUEST_STRING_PARAMETER,
            NRPN_ADDRESS_PAGE_STRINGS,
            _NRPN_STRING_PARAMETER_ID_RIG_COMMENT
        ),
        response = KemperNRPNMessage(
            NRPN_FUNCTION_RESPONSE_STRING_PARAMETER, 
            NRPN_ADDRESS_PAGE_STRINGS,
            _NRPN_STRING_PARAMETER_ID_RIG_COMMENT
        ),
        type = ClientParameterMapping.PARAMETER_TYPE_STRING
    )

# Rig date (request only)
def MAPPING_RIG_DATE(): 
    return ClientParameterMapping(
        name = "Rig Date",
        request = KemperNRPNMessage(               
            NRPN_FUNCTION_REQUEST_STRING_PARAMETER, 
            NRPN_ADDRESS_PAGE_STRINGS,
            _NRPN_STRING_PARAMETER_ID_RIG_DATE
        ),
        response = KemperNRPNMessage(
            NRPN_FUNCTION_RESPONSE_STRING_PARAMETER, 
            NRPN_ADDRESS_PAGE_STRINGS,
            _NRPN_STRING_PARAMETER_ID_RIG_DATE
        ),
        type = ClientParameterMapping.PARAMETER_TYPE_STRING
    )

# Rig volume
def MAPPING_RIG_VOLUME(): 
    return ClientParameterMapping(
        name = "Rig Volume",
        set = KemperNRPNMessage(
            NRPN_FUNCTION_SET_SINGLE_PARAMETER, 
            _NRPN_ADDRESS_PAGE_RIG_PARAMETERS,
            _NRPN_RIG_PARAMETER_VOLUME
        ),
        request = KemperNRPNMessage(
            NRPN_FUNCTION_REQUEST_SINGLE_PARAMETER,
            _NRPN_ADDRESS_PAGE_RIG_PARAMETERS,
            _NRPN_RIG_PARAMETER_VOLUME
        ),
        response = KemperNRPNMessage(
            NRPN_FUNCTION_RESPONSE_SINGLE_PARAMETER,
            _NRPN_ADDRESS_PAGE_RIG_PARAMETERS,
            _NRPN_RIG_PARAMETER_VOLUME
        )
    )