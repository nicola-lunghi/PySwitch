# from .. import KemperNRPNExtendedMessage
# from ....controller.client import ClientParameterMapping
# from .. import NRPN_FUNCTION_RESPONSE_STRING_PARAMETER, NRPN_FUNCTION_REQUEST_EXT_STRING_PARAMETER

# # Slot Name. Slot must be in range [1..5]
# def MAPPING_SLOT_NAME(slot): 
#     return ClientParameterMapping.get(
#         name = f"Slot Name { str(slot) }",
#         request = KemperNRPNExtendedMessage(               
#             NRPN_FUNCTION_REQUEST_EXT_STRING_PARAMETER,
#             [0, 0, 1, 0, slot]
#         ),
#         response = KemperNRPNExtendedMessage(
#             NRPN_FUNCTION_RESPONSE_STRING_PARAMETER,
#             [0, 0, 1, 0, slot]
#         ),
#         type = ClientParameterMapping.PARAMETER_TYPE_STRING
#     )
