#################################################################################################################################
# 
# Global kemper configuration for the KemperStomp script: definitions of kemper MIDI addresses, effect categories and a defaulted
# SysEx message class to be used in mappings for convenience. The MIDI message composition/parsing is also implemented here.
#
#################################################################################################################################


# Kemper MIDI specification related definitions.
class KemperMidi:
    
    # IDs for the available effect slots
    EFFECT_SLOT_ID_A = 0
    EFFECT_SLOT_ID_B = 1
    EFFECT_SLOT_ID_C = 2
    EFFECT_SLOT_ID_D = 3
    EFFECT_SLOT_ID_X = 4
    EFFECT_SLOT_ID_MOD = 5
    EFFECT_SLOT_ID_DLY = 6
    EFFECT_SLOT_ID_REV = 7

    # Slot enable/disable. Order has to match the one defined above!
    CC_EFFECT_SLOT_ENABLE = (
        17,    # Slot A
        18,    # Slot B
        19,    # Slot C
        20,    # Slot D

        22,    # Slot X
        24,    # Slot MOD        
        27,    # Slot DLY (with Spillover)        
        29     # Slot REV (with Spillover)
    )

    CC_TUNER_MODE = 31
    CC_BANK_INCREASE = 48
    CC_BANK_DECREASE = 49
    CC_RIG_SELECT = 50       # This selects slot 1 of the current bank. The slots 2-5 can be addressed by adding (n-1) to the value.
    CC_BANK_PRESELECT = 47
    CC_TAP_TEMPO = 30
    CC_ROTARY_SPEED = 33     # 1 = Fast, 0 = Slow

    # Values for CC commands
    CC_VALUE_BANK_CHANGE = 0

    # Product types
    NRPN_PRODUCT_TYPE_PROFILER = 0x00         # Kemper Profiler
    NRPN_PRODUCT_TYPE_PROFILER_PLAYER = 0x02  # Kemper Profiler Player

    # Device IDs
    NRPN_DEVICE_ID_OMNI = 0x7f

    # Parameter types
    NRPN_PARAMETER_TYPE_NUMERIC = 0   # Default, also used for on/off
    NRPN_PARAMETER_TYPE_STRING = 1

    # Slot address pages. Order has to match the one defined above!
    NRPN_SLOT_ADDRESS_PAGE = (
        0x32,   # Slot A
        0x33,   # Slot B
        0x34,   # Slot C
        0x35,   # Slot D

        0x38,   # Slot X
        0x3a,   # Slot MOD
        0x3c,   # Slot DLY
        0x3d    # Slot REV
    )    

    # Other adress pages
    NRPN_ADDRESS_PAGE_STRINGS = 0x00
    NRPN_ADDRESS_PAGE_RIG_PARAMETERS = 0x04
    NRPN_ADDRESS_PAGE_FREEZE = 0x7d
    NRPN_ADDRESS_PAGE_AMP = 0x0a
    NRPN_ADDRESS_PAGE_CABINET = 0x0c

    # Generally used NRPN values
    NRPN_MANUFACTURER_ID = [0x00, 0x20, 0x33]             # Kemper manufacturer ID
    NRPN_INSTANCE = 0x00                                  # Instance ID for NRPN. The profiler only supports instance 0.
    NRPN_PARAMETER_OFF = 0
    NRPN_PARAMETER_ON = 1

    # NRPN Function codes
    NRPN_FUNCTION_REQUEST_SINGLE_PARAMETER = 0x41
    NRPN_FUNCTION_REQUEST_STRING_PARAMETER = 0x43

    NRPN_FUNCTION_RESPONSE_SINGLE_PARAMETER = 0x01
    NRPN_FUNCTION_RESPONSE_STRING_PARAMETER = 0x03

    NRPN_FUNCTION_SET_SINGLE_PARAMETER = 0x01

    # NRPN parameters for effect slots
    NRPN_EFFECT_PARAMETER_ADDRESS_TYPE = 0x00   
    NRPN_EFFECT_PARAMETER_ADDRESS_ON_OFF = 0x03    
    NRPN_EFFECT_PARAMETER_ADDRESS_ROTARY_SPEED = 0x1e
    # ... TODO add further parameters here

    # Rig parameters (page 0x04)
    NRPN_RIG_PARAMETER_VOLUME = 0x01
    # ... TODO add further parameters here

    # Amp parameters (page 0x0a)
    NRPN_AMP_PARAMETER_ON_OFF = 0x02
    
    # Cab parameters (page 0x0c)
    NRPN_CABINET_PARAMETER_ON_OFF = 0x02

    # NRPN String parameters
    NRPN_STRING_PARAMETER_ID_RIG_NAME = 0x01
    NRPN_STRING_PARAMETER_ID_RIG_DATE = 0x03
    NRPN_STRING_PARAMETER_ID_AMP_NAME = 0x10
    NRPN_STRING_PARAMETER_ID_CABINET_NAME = 0x20

    # Freeze parameter addresses on page 0x7d (Looper and Delay Freeze) for all slots. 
    # Order has to match the one defined above!
    NRPN_FREEZE_SLOT_PARAMETER_ADDRESSES = [
        0x6b,   # Slot A
        0x6c,   # Slot B
        0x6d,   # Slot C
        0x6e,   # Slot D

        0x6f,   # Slot X
        0x71,   # Slot MOD
        0x72,   # Slot DLY
        0x73    # Slot REV
    ]

    # Helper to convert values in range [0..1] to the NRPN value range of [0..16383]
    @staticmethod
    def NRPN_VALUE(value):
        return int(16383 * value)

