#################################################################################################################################
# 
# Global kemper configuration for the KemperStomp script: definitions of kemper MIDI addresses, effect categories and a defaulted
# SysEx message class to be used in mappings for convenience. The MIDI message composition/parsing is also implemented here.
#
#################################################################################################################################

import math

from adafruit_midi.control_change import ControlChange
from adafruit_midi.system_exclusive import SystemExclusive

from .definitions import Colors
from .src.client.Client import ClientValueProvider
from .src.controller.actions.EffectEnableAction import EffectCategoryProvider

#################################################################################################################################


# Kemper ui specific definitions
class KemperDefinitions:
    # Effect type color assignment
    EFFECT_COLOR_NONE = Colors.DEFAULT_LABEL_COLOR
    EFFECT_COLOR_WAH = Colors.ORANGE
    EFFECT_COLOR_DISTORTION = Colors.RED
    EFFECT_COLOR_COMPRESSOR = Colors.BLUE
    EFFECT_COLOR_NOISE_GATE = Colors.BLUE
    EFFECT_COLOR_SPACE = Colors.GREEN
    EFFECT_COLOR_CHORUS = Colors.BLUE
    EFFECT_COLOR_PHASER_FLANGER = Colors.PURPLE
    EFFECT_COLOR_EQUALIZER = Colors.YELLOW
    EFFECT_COLOR_BOOSTER = Colors.RED
    EFFECT_COLOR_LOOPER = Colors.PURPLE
    EFFECT_COLOR_PITCH = Colors.WHITE
    EFFECT_COLOR_DUAL = Colors.GREEN
    EFFECT_COLOR_DELAY = Colors.GREEN
    EFFECT_COLOR_REVERB = Colors.GREEN

    # Effect type display names
    EFFECT_NAME_NONE = "-"
    EFFECT_NAME_WAH = "Wah"
    EFFECT_NAME_DISTORTION = "Dist"
    EFFECT_NAME_COMPRESSOR = "Comp"
    EFFECT_NAME_NOISE_GATE = "Gate"
    EFFECT_NAME_SPACE = "Space"
    EFFECT_NAME_CHORUS = "Chorus"
    EFFECT_NAME_PHASER_FLANGER = "Phaser"
    EFFECT_NAME_EQUALIZER = "EQ"
    EFFECT_NAME_BOOSTER = "Boost"
    EFFECT_NAME_LOOPER = "Looper"
    EFFECT_NAME_PITCH = "Pitch"
    EFFECT_NAME_DUAL = "Dual"
    EFFECT_NAME_DELAY = "Delay"
    EFFECT_NAME_REVERB = "Reverb"

    # Colors for special modes
    TUNER_MODE_COLOR = Colors.WHITE


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


################################################################################################################################


# Provides mapping of the kemper internal effect types to effect categories
class KemperEffectCategories(EffectCategoryProvider):

    # Effect types enum (used internally, also for indexing colors, so be sure these are always a row from 0 to n)
    CATEGORY_NONE = 0
    CATEGORY_WAH = 1
    CATEGORY_DISTORTION = 2
    CATEGORY_COMPRESSOR = 3
    CATEGORY_NOISE_GATE = 4
    CATEGORY_SPACE = 5
    CATEGORY_CHORUS = 6
    CATEGORY_PHASER_FLANGER = 7
    CATEGORY_EQUALIZER = 8
    CATEGORY_BOOSTER = 9
    CATEGORY_LOOPER = 10
    CATEGORY_PITCH = 11
    CATEGORY_DUAL = 12
    CATEGORY_DELAY = 13
    CATEGORY_REVERB = 14

    # Effect colors. The order must match the enums for the effect types defined above!
    CATEGORY_COLORS = [
        KemperDefinitions.EFFECT_COLOR_NONE,
        KemperDefinitions.EFFECT_COLOR_WAH,
        KemperDefinitions.EFFECT_COLOR_DISTORTION,
        KemperDefinitions.EFFECT_COLOR_COMPRESSOR,
        KemperDefinitions.EFFECT_COLOR_NOISE_GATE,
        KemperDefinitions.EFFECT_COLOR_SPACE,
        KemperDefinitions.EFFECT_COLOR_CHORUS,
        KemperDefinitions.EFFECT_COLOR_PHASER_FLANGER,
        KemperDefinitions.EFFECT_COLOR_EQUALIZER,
        KemperDefinitions.EFFECT_COLOR_BOOSTER,
        KemperDefinitions.EFFECT_COLOR_LOOPER,
        KemperDefinitions.EFFECT_COLOR_PITCH,
        KemperDefinitions.EFFECT_COLOR_DUAL,
        KemperDefinitions.EFFECT_COLOR_DELAY,
        KemperDefinitions.EFFECT_COLOR_REVERB
    ]

    # Effect type display names. The order must match the enums for the effect types defined above!
    CATEGORY_NAMES = [
        KemperDefinitions.EFFECT_NAME_NONE,
        KemperDefinitions.EFFECT_NAME_WAH,
        KemperDefinitions.EFFECT_NAME_DISTORTION,
        KemperDefinitions.EFFECT_NAME_COMPRESSOR,
        KemperDefinitions.EFFECT_NAME_NOISE_GATE,
        KemperDefinitions.EFFECT_NAME_SPACE,
        KemperDefinitions.EFFECT_NAME_CHORUS,
        KemperDefinitions.EFFECT_NAME_PHASER_FLANGER,
        KemperDefinitions.EFFECT_NAME_EQUALIZER,
        KemperDefinitions.EFFECT_NAME_BOOSTER,
        KemperDefinitions.EFFECT_NAME_LOOPER,
        KemperDefinitions.EFFECT_NAME_PITCH,
        KemperDefinitions.EFFECT_NAME_DUAL,
        KemperDefinitions.EFFECT_NAME_DELAY,
        KemperDefinitions.EFFECT_NAME_REVERB
    ]

    # Must return the effect category for a mapping value
    def get_effect_category(self, kpp_effect_type):
        # NOTE: The ranges are defined by Kemper with a lot of unused numbers, so the borders between types
        # could need to be adjusted with future Kemper firmware updates!
        if (kpp_effect_type == 0):
            return KemperEffectCategories.CATEGORY_NONE
        elif (0 < kpp_effect_type and kpp_effect_type <= 14):
            return KemperEffectCategories.CATEGORY_WAH
        elif (14 < kpp_effect_type and kpp_effect_type <= 45):
            return KemperEffectCategories.CATEGORY_DISTORTION
        elif (45 < kpp_effect_type and kpp_effect_type <= 55):
            return KemperEffectCategories.CATEGORY_COMPRESSOR
        elif (55 < kpp_effect_type and kpp_effect_type <= 60):
            return KemperEffectCategories.CATEGORY_NOISE_GATE       
        elif (60 < kpp_effect_type and kpp_effect_type <= 64):
            return KemperEffectCategories.CATEGORY_SPACE            
        elif (64 < kpp_effect_type and kpp_effect_type <= 80):
            return KemperEffectCategories.CATEGORY_CHORUS
        elif (80 < kpp_effect_type and kpp_effect_type <= 95):
            return KemperEffectCategories.CATEGORY_PHASER_FLANGER
        elif (95 < kpp_effect_type and kpp_effect_type <= 110):
            return KemperEffectCategories.CATEGORY_EQUALIZER
        elif (110 < kpp_effect_type and kpp_effect_type <= 120):
            return KemperEffectCategories.CATEGORY_BOOSTER
        elif (120 < kpp_effect_type and kpp_effect_type <= 125):
            return KemperEffectCategories.CATEGORY_LOOPER
        elif (125 < kpp_effect_type and kpp_effect_type <= 135):
            return KemperEffectCategories.CATEGORY_PITCH
        elif (135 < kpp_effect_type and kpp_effect_type <= 143):
            return KemperEffectCategories.CATEGORY_DUAL
        elif (143 < kpp_effect_type and kpp_effect_type <= 170):
            return KemperEffectCategories.CATEGORY_DELAY
        else:
            return KemperEffectCategories.CATEGORY_REVERB
    
    # Must return the effect color for a mapping value
    def get_effect_category_color(self, kpp_effect_type):
        return KemperEffectCategories.CATEGORY_COLORS[kpp_effect_type]
    
    # Must return the effect name for a mapping value
    def get_effect_category_name(self, kpp_effect_type):
        return KemperEffectCategories.CATEGORY_NAMES[kpp_effect_type]
    
    # Must return the value interpreted as "not assigned"
    def get_category_not_assigned(self):
        return KemperEffectCategories.CATEGORY_NONE


################################################################################################################################


# Kemper specific SysEx message with defaults which are valid most of the time
class KemperNRPNMessage(SystemExclusive):
    # Takes MIDI messages as argument (CC or SysEx)
    def __init__(
            self, 
            function_code,
            address_page,
            address_number,
            manufacturer_id = KemperMidi.NRPN_MANUFACTURER_ID, 
            product_type = KemperMidi.NRPN_PRODUCT_TYPE_PROFILER_PLAYER,
            device_id = KemperMidi.NRPN_DEVICE_ID_OMNI
        ):

        # Adafruit SystemExclusive
        super().__init__(
            manufacturer_id,                 # [0x00, 0x20, 0x33]
            [
                product_type,                # 0x02 (Player), 0x00 (Profiler)
                device_id,                   # 0x7f (omni) or manually set via parameter
                function_code,               # Selects the function, for example 0x41 for requesting a single parameter
                KemperMidi.NRPN_INSTANCE,    # 0x00
                address_page,                # Controller MSB (address page)
                address_number               # Controller LSB (address number of parameter)
            ]
        )
        

################################################################################################################################


# Implements setting values and parsing request responses
class KemperMidiValueProvider(ClientValueProvider):

    # Must parse the incoming MIDI message and return the value contained.
    # If the response template does not match, must return None.
    # Must return True to notify the listeners of a value change.
    def parse(self, mapping, midi_message):
        # Compare manufacturer IDs
        if midi_message.manufacturer_id != mapping.response.manufacturer_id:
            return False
        
        # Get data as integer list from both the incoming message and the response
        # template in the mapping (both messages are SysEx anytime)
        response = list(midi_message.data)                        
        template = list(mapping.response.data)        

        # The first two values are ignored (the Kemper MIDI specification implies this would contain the product type
        # and device ID as for the request, however the device just sends two zeroes)

        # Check if the message belongs to the mapping. The following have to match:
        #   2: function code, 
        #   3: instance ID, 
        #   4: address page, 
        #   5: address nunber
        if response[2:6] != template[2:6]:
            return False
        
        # The values starting from index 6 are the value of the response.
        if mapping.type == KemperMidi.NRPN_PARAMETER_TYPE_STRING:
            # Take as string
            mapping.value = ''.join(chr(int(c)) for c in response[6:-1])
        else:
            # Decode 14-bit value to int
            mapping.value = response[-2] * 128 + response[-1]

        return True
    
    # Must set the passed value on the SET message of the mapping.
    def set_value(self, mapping, value):
        if isinstance(mapping.set, ControlChange):
            # Set value directly (CC takes int values)
            mapping.set.value = value

        elif isinstance(mapping.set, SystemExclusive):            
            # Fill up message to appropriate length for the specification
            data = list(mapping.set.data)
            while len(data) < 8:
                data.append(0)
            
            # Set value as 14 bit
            data[6] = int(math.floor(value / 128))
            data[7] = int(value % 128)

            mapping.set.data = bytes(data)
        
