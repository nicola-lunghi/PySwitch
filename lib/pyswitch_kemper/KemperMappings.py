#################################################################################################################################
# 
# Defines some useful MIDI mappings.
#
#################################################################################################################################
 
from adafruit_midi.control_change import ControlChange

from .KemperNRPNMessage import KemperNRPNMessage
from .KemperSlot import KemperSlot

from .Kemper import Kemper

from pyswitch.core.client.ClientParameterMapping import ClientParameterMapping

#################################################################################################################################

# CC Addresses
CC_TUNER_MODE = 31
CC_BANK_INCREASE = 48
CC_BANK_DECREASE = 49
CC_RIG_SELECT = 50       # This selects slot 1 of the current bank. The slots 2-5 can be addressed by adding (n-1) to the value.
CC_BANK_PRESELECT = 47
CC_TAP_TEMPO = 30
CC_ROTARY_SPEED = 33     # 1 = Fast, 0 = Slow

# Adress pages
NRPN_ADDRESS_PAGE_STRINGS = 0x00
NRPN_ADDRESS_PAGE_RIG_PARAMETERS = 0x04
NRPN_ADDRESS_PAGE_FREEZE = 0x7d
NRPN_ADDRESS_PAGE_AMP = 0x0a
NRPN_ADDRESS_PAGE_CABINET = 0x0c

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

#################################################################################################################################


# Defines some useful MIDI mappings
class KemperMappings:

    # Effect slot enable/disable
    @staticmethod
    def EFFECT_SLOT_ON_OFF(slot_id):
        return ClientParameterMapping(
            name = "Effect Status " + str(slot_id),
            set = ControlChange(
                KemperSlot.CC_EFFECT_SLOT_ENABLE[slot_id], 
                0    # Dummy value, will be overridden
            ),
            request = KemperNRPNMessage(               
                NRPN_FUNCTION_REQUEST_SINGLE_PARAMETER, 
                KemperSlot.NRPN_SLOT_ADDRESS_PAGE[slot_id],
                NRPN_EFFECT_PARAMETER_ADDRESS_ON_OFF
            ),
            response = KemperNRPNMessage(
                NRPN_FUNCTION_RESPONSE_SINGLE_PARAMETER,
                KemperSlot.NRPN_SLOT_ADDRESS_PAGE[slot_id],
                NRPN_EFFECT_PARAMETER_ADDRESS_ON_OFF
            )
        )
    
    # Effect slot type (request only)
    @staticmethod
    def EFFECT_SLOT_TYPE(slot_id):
        return ClientParameterMapping(
            name = "Effect Type " + str(slot_id),
            request = KemperNRPNMessage(               
                NRPN_FUNCTION_REQUEST_SINGLE_PARAMETER, 
                KemperSlot.NRPN_SLOT_ADDRESS_PAGE[slot_id],
                NRPN_EFFECT_PARAMETER_ADDRESS_TYPE
            ),
            response = KemperNRPNMessage(               
                NRPN_FUNCTION_RESPONSE_SINGLE_PARAMETER, 
                KemperSlot.NRPN_SLOT_ADDRESS_PAGE[slot_id],
                NRPN_EFFECT_PARAMETER_ADDRESS_TYPE
            )
        )

   # Rotary speed (fast/slow)
    @staticmethod
    def ROTARY_SPEED(slot_id):
        return ClientParameterMapping(
            name = "Rotary Speed " + str(slot_id),
            set = KemperNRPNMessage(
                NRPN_FUNCTION_SET_SINGLE_PARAMETER, 
                KemperSlot.NRPN_SLOT_ADDRESS_PAGE[slot_id],
                NRPN_EFFECT_PARAMETER_ADDRESS_ROTARY_SPEED
            ),
            request = KemperNRPNMessage(               
                NRPN_FUNCTION_REQUEST_SINGLE_PARAMETER, 
                KemperSlot.NRPN_SLOT_ADDRESS_PAGE[slot_id],
                NRPN_EFFECT_PARAMETER_ADDRESS_ROTARY_SPEED
            ),
            response = KemperNRPNMessage(
                NRPN_FUNCTION_RESPONSE_SINGLE_PARAMETER,
                KemperSlot.NRPN_SLOT_ADDRESS_PAGE[slot_id],
                NRPN_EFFECT_PARAMETER_ADDRESS_ROTARY_SPEED
            )
        )

    # Freeze for slot
    @staticmethod
    def FREEZE(slot_id):
        return ClientParameterMapping(
            name = "Freeze " + str(slot_id),
            set = KemperNRPNMessage(
                NRPN_FUNCTION_SET_SINGLE_PARAMETER, 
                NRPN_ADDRESS_PAGE_FREEZE,
                KemperSlot.NRPN_FREEZE_SLOT_PARAMETER_ADDRESSES[slot_id]
            ),
            request = KemperNRPNMessage(               
                NRPN_FUNCTION_REQUEST_SINGLE_PARAMETER, 
                NRPN_ADDRESS_PAGE_FREEZE,
                KemperSlot.NRPN_FREEZE_SLOT_PARAMETER_ADDRESSES[slot_id]
            ),
            response = KemperNRPNMessage(               
                NRPN_FUNCTION_RESPONSE_SINGLE_PARAMETER, 
                NRPN_ADDRESS_PAGE_FREEZE,
                KemperSlot.NRPN_FREEZE_SLOT_PARAMETER_ADDRESSES[slot_id]
            )
        )

    # Rig name (request only)
    RIG_NAME = ClientParameterMapping(
        name = "Rig Name",
        request = KemperNRPNMessage(               
            NRPN_FUNCTION_REQUEST_STRING_PARAMETER, 
            NRPN_ADDRESS_PAGE_STRINGS,
            NRPN_STRING_PARAMETER_ID_RIG_NAME
        ),
        response = KemperNRPNMessage(
            NRPN_FUNCTION_RESPONSE_STRING_PARAMETER, 
            NRPN_ADDRESS_PAGE_STRINGS,
            NRPN_STRING_PARAMETER_ID_RIG_NAME
        ),
        type = Kemper.NRPN_PARAMETER_TYPE_STRING
    )

    # Rig date (request only)
    RIG_DATE = ClientParameterMapping(
        name = "Rig Date",
        request = KemperNRPNMessage(               
            NRPN_FUNCTION_REQUEST_STRING_PARAMETER, 
            NRPN_ADDRESS_PAGE_STRINGS,
            NRPN_STRING_PARAMETER_ID_RIG_DATE
        ),
        response = KemperNRPNMessage(
            NRPN_FUNCTION_RESPONSE_STRING_PARAMETER, 
            NRPN_ADDRESS_PAGE_STRINGS,
            NRPN_STRING_PARAMETER_ID_RIG_DATE
        ),
        type = Kemper.NRPN_PARAMETER_TYPE_STRING
    )

    # Switch tuner mode on/off (no receive possible!)
    TUNER_MODE_ON_OFF = ClientParameterMapping(
        name = "Tuner Mode",
        set = ControlChange(
            CC_TUNER_MODE, 
            0    # Dummy value, will be overridden
        )
    )

    # Switch tuner mode on/off (no receive possible!)
    TAP_TEMPO = ClientParameterMapping(
        name = "Tap Tempo",
        set = ControlChange(
            CC_TAP_TEMPO, 
            0    # Dummy value, will be overridden
        )
    )

    # Rig volume
    RIG_VOLUME = ClientParameterMapping(
        name = "Rig Volume",
        set = KemperNRPNMessage(
            NRPN_FUNCTION_SET_SINGLE_PARAMETER, 
            NRPN_ADDRESS_PAGE_RIG_PARAMETERS,
            NRPN_RIG_PARAMETER_VOLUME
        ),
        request = KemperNRPNMessage(
            NRPN_FUNCTION_REQUEST_SINGLE_PARAMETER,
            NRPN_ADDRESS_PAGE_RIG_PARAMETERS,
            NRPN_RIG_PARAMETER_VOLUME
        ),
        response = KemperNRPNMessage(
            NRPN_FUNCTION_RESPONSE_SINGLE_PARAMETER,
            NRPN_ADDRESS_PAGE_RIG_PARAMETERS,
            NRPN_RIG_PARAMETER_VOLUME
        )
    )

    # Amp name (request only)
    AMP_NAME = ClientParameterMapping(
        name = "Amp Name",
        request = KemperNRPNMessage(               
            NRPN_FUNCTION_REQUEST_STRING_PARAMETER, 
            NRPN_ADDRESS_PAGE_STRINGS,
            NRPN_STRING_PARAMETER_ID_AMP_NAME
        ),
        response = KemperNRPNMessage(
            NRPN_FUNCTION_RESPONSE_STRING_PARAMETER, 
            NRPN_ADDRESS_PAGE_STRINGS,
            NRPN_STRING_PARAMETER_ID_AMP_NAME
        ),
        type = Kemper.NRPN_PARAMETER_TYPE_STRING
    )

    # Amp on/off
    AMP_ON_OFF = ClientParameterMapping(
        name = "Amp Status",
        set = KemperNRPNMessage(
            NRPN_FUNCTION_SET_SINGLE_PARAMETER, 
            NRPN_ADDRESS_PAGE_AMP,
            NRPN_AMP_PARAMETER_ON_OFF
        ),
        request = KemperNRPNMessage(
            NRPN_FUNCTION_REQUEST_SINGLE_PARAMETER,
            NRPN_ADDRESS_PAGE_AMP,
            NRPN_AMP_PARAMETER_ON_OFF
        ),
        response = KemperNRPNMessage(
            NRPN_FUNCTION_RESPONSE_SINGLE_PARAMETER,
            NRPN_ADDRESS_PAGE_AMP,
            NRPN_AMP_PARAMETER_ON_OFF
        )
    )

    # Cab name (request only)
    CABINET_NAME = ClientParameterMapping(
        name = "Cab Name",
        request = KemperNRPNMessage(               
            NRPN_FUNCTION_REQUEST_STRING_PARAMETER, 
            NRPN_ADDRESS_PAGE_STRINGS,
            NRPN_STRING_PARAMETER_ID_CABINET_NAME
        ),
        response = KemperNRPNMessage(
            NRPN_FUNCTION_RESPONSE_STRING_PARAMETER, 
            NRPN_ADDRESS_PAGE_STRINGS,
            NRPN_STRING_PARAMETER_ID_CABINET_NAME
        ),
        type = Kemper.NRPN_PARAMETER_TYPE_STRING
    )
    
    # Cab on/off
    CABINET_ON_OFF = ClientParameterMapping(
        name = "Cab Status",
        set = KemperNRPNMessage(
            NRPN_FUNCTION_SET_SINGLE_PARAMETER, 
            NRPN_ADDRESS_PAGE_CABINET,
            NRPN_CABINET_PARAMETER_ON_OFF
        ),
        request = KemperNRPNMessage(
            NRPN_FUNCTION_REQUEST_SINGLE_PARAMETER,
            NRPN_ADDRESS_PAGE_CABINET,
            NRPN_CABINET_PARAMETER_ON_OFF
        ),
        response = KemperNRPNMessage(
            NRPN_FUNCTION_RESPONSE_SINGLE_PARAMETER,
            NRPN_ADDRESS_PAGE_CABINET,
            NRPN_CABINET_PARAMETER_ON_OFF
        )
    )

    NEXT_BANK = ClientParameterMapping(
        name = "Next Bank",
        set = ControlChange(
            CC_BANK_INCREASE,
            0    # Dummy value, will be overridden
        )
    )

    PREVIOUS_BANK = ClientParameterMapping(
        name = "Prev Bank",
        set = ControlChange(
            CC_BANK_DECREASE,
            0    # Dummy value, will be overridden
        )
    )

    # Selects a rig inside the current bank. Rig index must be in range [0..4]
    @staticmethod
    def RIG_SELECT(rig):
        return ClientParameterMapping(
            name = "Rig Select",
            set = ControlChange(
                CC_RIG_SELECT + rig,
                0    # Dummy value, will be overridden
            )
        )
    
    # Pre-selects a bank. CHanges will take effect when the next RIG_SELECT message is sent.
    # Bank index must be in range [0..124]
    BANK_PRESELECT = ClientParameterMapping(
        name = "Bank Preselect",
        set = ControlChange(
            CC_BANK_PRESELECT,
            0    # Dummy value, will be overridden
        )
    )
    
    

