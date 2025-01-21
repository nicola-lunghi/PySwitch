from micropython import const
from .. import KemperParameterMapping, KemperNRPNMessage
from .. import NRPN_FUNCTION_SET_SINGLE_PARAMETER, NRPN_FUNCTION_REQUEST_STRING_PARAMETER, NRPN_FUNCTION_REQUEST_SINGLE_PARAMETER, NRPN_FUNCTION_RESPONSE_SINGLE_PARAMETER, NRPN_ADDRESS_PAGE_STRINGS, NRPN_FUNCTION_RESPONSE_STRING_PARAMETER

_NRPN_ADDRESS_PAGE_AMP = const(0x0a)
_NRPN_AMP_PARAMETER_STATE = const(0x02)
_NRPN_STRING_PARAMETER_ID_AMP_NAME = const(0x10)

# Amp name (request only)
def MAPPING_AMP_NAME(): 
    return KemperParameterMapping(
        name = "Amp Name",
        request = KemperNRPNMessage(               
            NRPN_FUNCTION_REQUEST_STRING_PARAMETER, 
            NRPN_ADDRESS_PAGE_STRINGS,
            _NRPN_STRING_PARAMETER_ID_AMP_NAME
        ),
        response = KemperNRPNMessage(
            NRPN_FUNCTION_RESPONSE_STRING_PARAMETER, 
            NRPN_ADDRESS_PAGE_STRINGS,
            _NRPN_STRING_PARAMETER_ID_AMP_NAME
        ),
        type = KemperParameterMapping.PARAMETER_TYPE_STRING
    )

# Amp on/off
def MAPPING_AMP_STATE(): 
    return KemperParameterMapping(
        name = "Amp State",
        set = KemperNRPNMessage(
            NRPN_FUNCTION_SET_SINGLE_PARAMETER, 
            _NRPN_ADDRESS_PAGE_AMP,
            _NRPN_AMP_PARAMETER_STATE
        ),
        request = KemperNRPNMessage(
            NRPN_FUNCTION_REQUEST_SINGLE_PARAMETER,
            _NRPN_ADDRESS_PAGE_AMP,
            _NRPN_AMP_PARAMETER_STATE
        ),
        response = KemperNRPNMessage(
            NRPN_FUNCTION_RESPONSE_SINGLE_PARAMETER,
            _NRPN_ADDRESS_PAGE_AMP,
            _NRPN_AMP_PARAMETER_STATE
        )
    )
