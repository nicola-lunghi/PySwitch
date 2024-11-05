from math import floor

from adafruit_midi.control_change import ControlChange
from adafruit_midi.system_exclusive import SystemExclusive

from pyswitch.misc import Colors, Defaults, PeriodCounter, Tools
from pyswitch.controller.actions.actions import ParameterAction, PushButtonModes
from pyswitch.controller.Client import ClientParameterMapping

from pyswitch.controller.actions.actions import EffectEnableAction, ParameterAction, ResetDisplaysAction

####################################################################################################################

# Definitions of devices
NRPN_PRODUCT_TYPE_PROFILER = 0x00                     # Kemper Profiler
NRPN_PRODUCT_TYPE_PROFILER_PLAYER = 0x02              # Kemper Profiler Player

# This defines which type of device to control
NRPN_PRODUCT_TYPE = NRPN_PRODUCT_TYPE_PROFILER_PLAYER

####################################################################################################################

# CC Addresses
CC_TUNER_MODE = 31
CC_BANK_INCREASE = 48
CC_BANK_DECREASE = 49
CC_RIG_SELECT = 50       # This selects slot 1 of the current bank. The slots 2-5 can be addressed by adding (n-1) to the value.
CC_BANK_PRESELECT = 47
CC_TAP_TEMPO = 30
CC_ROTARY_SPEED = 33     # 1 = Fast, 0 = Slow

CC_VALUE_BANK_CHANGE = 0

# Basic values for all NRPN messages
NRPN_MANUFACTURER_ID = [0x00, 0x20, 0x33]             # Kemper manufacturer ID
NRPN_DEVICE_ID_OMNI = 0x7f                            # Omni (all devices, only supported mode)
NRPN_INSTANCE = 0x00                                  # Instance ID for NRPN. The profiler only supports instance 0.

# NRPN Adress pages
NRPN_ADDRESS_PAGE_STRINGS = 0x00
NRPN_ADDRESS_PAGE_RIG_PARAMETERS = 0x04
NRPN_ADDRESS_PAGE_FREEZE = 0x7d
NRPN_ADDRESS_PAGE_AMP = 0x0a
NRPN_ADDRESS_PAGE_CABINET = 0x0c

# NRPN Function codes
NRPN_FUNCTION_REQUEST_SINGLE_PARAMETER = 0x41
NRPN_FUNCTION_REQUEST_STRING_PARAMETER = 0x43
NRPN_FUNCTION_REQUEST_EXT_STRING_PARAMETER = 0x47

NRPN_FUNCTION_RESPONSE_SINGLE_PARAMETER = 0x01
NRPN_FUNCTION_RESPONSE_STRING_PARAMETER = 0x03

NRPN_FUNCTION_SET_SINGLE_PARAMETER = 0x01

# NRPN parameters for effect slots
NRPN_EFFECT_PARAMETER_ADDRESS_TYPE = 0x00   
NRPN_EFFECT_PARAMETER_ADDRESS_STATE = 0x03    
NRPN_EFFECT_PARAMETER_ADDRESS_ROTARY_SPEED = 0x1e
# ... add further parameters here

# Rig parameters (page 0x04)
NRPN_RIG_PARAMETER_VOLUME = 0x01
# ... add further parameters here

# Amp parameters (page 0x0a)
NRPN_AMP_PARAMETER_STATE = 0x02

# Cab parameters (page 0x0c)
NRPN_CABINET_PARAMETER_STATE = 0x02

# NRPN String parameters
NRPN_STRING_PARAMETER_ID_RIG_NAME = 0x01
NRPN_STRING_PARAMETER_ID_RIG_DATE = 0x03
NRPN_STRING_PARAMETER_ID_AMP_NAME = 0x10
NRPN_STRING_PARAMETER_ID_CABINET_NAME = 0x20

# Generally used NRPN values
NRPN_PARAMETER_OFF = 0
NRPN_PARAMETER_ON = 1


####################################################################################################################


# Kemper Effect slot IDs, MIDI addresses and display properties
class KemperEffectSlot:
    
    # IDs for the available effect slots
    EFFECT_SLOT_ID_A = 0
    EFFECT_SLOT_ID_B = 1
    EFFECT_SLOT_ID_C = 2
    EFFECT_SLOT_ID_D = 3
    
    EFFECT_SLOT_ID_X = 4
    EFFECT_SLOT_ID_MOD = 5
    EFFECT_SLOT_ID_DLY = 6
    EFFECT_SLOT_ID_REV = 7

    # CC Address for Effect Slot enable/disable. Order has to match the one defined above!
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

     # Slot names for display. Order has to match the one defined above!
    EFFECT_SLOT_NAMES = [
        "A",
        "B",
        "C",
        "D",

        "X",
        "MOD",
        "DLY",
        "REV"
    ]

    def __init__(self, slot_id):
        self._slot_id = slot_id

    # Must return the lot name
    def get_name(self):
        return KemperEffectSlot.EFFECT_SLOT_NAMES[self._slot_id]
    

####################################################################################################################

# All defined actions here have one parameter in common: A display definition (see definitions.py)
# which assigns a display label to the action (optional: If omitted, no visual feedback is given 
# on the display).
class KemperActionDefinitions: 

    ## Effect slots ########################################################################################################

    # Switch an effect slot on / off
    @staticmethod
    def EFFECT_STATE(slot_id, display = None, mode = PushButtonModes.HOLD_MOMENTARY, id = False):
        return EffectEnableAction({
            "mapping": KemperMappings.EFFECT_STATE(slot_id),
            "mappingType": KemperMappings.EFFECT_TYPE(slot_id),
            "categories": KemperEffectCategories(),
            "slotInfo": KemperEffectSlot(slot_id),
            "mode": mode,
            "display": display,
            "id": id
        })

    # Rotary speed (fast/slow)
    @staticmethod
    def ROTARY_SPEED(slot_id, display = None, color = Colors.DARK_BLUE, id = False):
        return ParameterAction({
            "mapping": KemperMappings.ROTARY_SPEED(slot_id),
            "display": display,
            "text": "Fast",
            "color": color,
            "id": id
        })

    ## Special functions ####################################################################################################

    # Switch tuner mode on / off
    @staticmethod
    def TUNER_MODE(display = None, color = Defaults.DEFAULT_SWITCH_COLOR, id = False):
        return ParameterAction({
            "mapping": KemperMappings.TUNER_MODE_STATE,
            "display": display,
            "text": "Tuner",
            "color": Colors.WHITE,
            "color": color,
            "id": id
        })

    # Tap tempo
    @staticmethod
    def TAP_TEMPO(display = None, color = Colors.DARK_GREEN, id = False):
        return ParameterAction({
            "mapping": KemperMappings.TAP_TEMPO,
            "display": display,
            "text": "Tap",
            "color": color,
            "mode": PushButtonModes.MOMENTARY,
            "id": id
        })

    ## Rig specific ##########################################################################################################

    # Volume boost function, based on setting rig volume to a certain boost value. To 
    # make sense, all rig volumes have to be zero in your rigs! You can then set the
    # boost rig volume by passing a value in range [0..1] (corresponding to the range of the
    # rig volume paramneter: 0.5 is 0dB, 0.75 is +6dB, 1.0 is +12dB)
    @staticmethod
    def RIG_VOLUME_BOOST(boost_volume, display = None, mode = PushButtonModes.HOLD_MOMENTARY, color = Colors.PINK, id = False):
        return ParameterAction({
            "mode": mode,
            "mapping": KemperMappings.RIG_VOLUME,
            "valueEnabled": KemperMidiValueProvider.NRPN_VALUE(boost_volume),
            "valueDisabled": KemperMidiValueProvider.NRPN_VALUE(0.5),           # 0dB
            "display": display,
            "text": "RigBoost",
            "color": color,
            "id": id
        })

    # Used to reset the screen areas which show rig info details directly after rig changes (if you dont use this, 
    # you get no visual feedback on the device that a new rig is coming up)
    @staticmethod
    def RESET_RIG_INFO_DISPLAYS(id = False):
        return ResetDisplaysAction({
            "resetSwitches": True,
            "ignoreOwnSwitch": True,
            "resetDisplayAreas": True,
            "id": id
        })

    ## Amp ########################################################################################################################

    # Amp on/off
    @staticmethod
    def AMP_STATE(display = None, mode = PushButtonModes.HOLD_MOMENTARY, color = Defaults.DEFAULT_SWITCH_COLOR, id = False):
        return ParameterAction({
            "mapping": KemperMappings.AMP_STATE,
            "mode": mode,
            "display": display,
            "text": "Amp",
            "color": color,
            "id": id
        })

    ## Cab ########################################################################################################################

    # Amp on/off
    @staticmethod
    def CABINET_STATE(display = None, mode = PushButtonModes.HOLD_MOMENTARY, color = Defaults.DEFAULT_SWITCH_COLOR, id = False):
        return ParameterAction({
            "mapping": KemperMappings.CABINET_STATE,
            "mode": mode,
            "display": display,
            "text": "Cab",
            "color": color,
            "id": id
        })

    ## Change Rig/Bank ############################################################################################################

    # Next bank (keeps rig index)
    @staticmethod
    def BANK_UP(display = None, color = Colors.WHITE, id = False):
        return ParameterAction({
            "mapping": KemperMappings.NEXT_BANK,
            "mode": PushButtonModes.ONE_SHOT,
            "valueEnabled": CC_VALUE_BANK_CHANGE,
            "display": display,
            "text": "Bank up",
            "color": color,
            "id": id
        })
    
    # Previous bank (keeps rig index)
    @staticmethod
    def BANK_DOWN(display = None, color = Colors.WHITE, id = False):
        return ParameterAction({
            "mapping": KemperMappings.PREVIOUS_BANK,
            "mode": PushButtonModes.ONE_SHOT,
            "valueEnabled": CC_VALUE_BANK_CHANGE,
            "display": display,
            "text": "Bank dn",
            "color": color,
            "id": id
        })
    
    # Selects a specific rig, or toggles between two rigs (if rig_off is also provided) in
    # the current bank. Rigs are indexed starting from one, range: [1..5].
    # Optionally, banks can be switched too in the same logic using bank and bank_off.
    @staticmethod
    def RIG_SELECT(rig, rig_off = None, bank = None, bank_off = None, display = None, color = Colors.YELLOW, id = False):
        # Texts always show the rig to be selected when the switch is pushed the next time
        text_rig_off = str(rig)
        text_rig_on = text_rig_off

        # Mappings and values: Start with a configuration for rig_off == None and bank(_off) = None.
        mapping = [
            ClientParameterMapping(),           # Dummy to be replaced by bank select if specified
            KemperMappings.RIG_SELECT(rig - 1)
        ]
        mapping_disable = [
            ClientParameterMapping(),           # Dummy to be replaced by bank select if specified
            KemperMappings.RIG_SELECT(rig - 1)
        ]
        value_enabled = [
            0,                                  # Dummy to be replaced by bank select if specified
            NRPN_PARAMETER_ON
        ]
        value_disabled = [
            0,                                  # Dummy to be replaced by bank select if specified
            NRPN_PARAMETER_ON
        ]

        # Bank for main rig
        if bank != None:
            mapping[0] = KemperMappings.BANK_PRESELECT
            if rig_off == None:
                mapping_disable[0] = KemperMappings.BANK_PRESELECT
            
            value_enabled[0] = bank - 1
            value_disabled[0] = bank - 1
            
            text_rig_off = str(bank) + "-" + text_rig_off
            if rig_off == None:
                text_rig_on = text_rig_off

        # Alternate rig (the rig selected when the switch state is False)
        if rig_off != None:
            # Use a different mapping for disabling
            mapping_disable[1] = KemperMappings.RIG_SELECT(rig_off - 1)
            text_rig_on = str(rig_off)

        # Bank for alternate rig
        if bank_off != None:
            if rig_off == None:
                raise Exception("RIG_SELECT: If bank_off is set, you must also provide rig_off.")
            
            mapping_disable[0] = KemperMappings.BANK_PRESELECT
            value_disabled[0] = bank_off - 1
            
            text_rig_on = str(bank_off) + "-" + text_rig_on

        # Finally we can create the action definition ;)
        return ParameterAction({
            "mapping": mapping,
            "mappingDisable": mapping_disable,
            "valueEnabled": value_enabled,
            "valueDisabled": value_disabled,
            "display": display,
            "text": "Rig " + text_rig_on,
            "textDisabled": "Rig " + text_rig_off,
            "color": color,
            "ledBrightness": {
                "on": ParameterAction.DEFAULT_LED_BRIGHTNESS_OFF,               # Set equal brightness (we do not need status display here)
                "off": ParameterAction.DEFAULT_LED_BRIGHTNESS_OFF
            },
            "displayDimFactorOn": ParameterAction.DEFAULT_SLOT_DIM_FACTOR_OFF,  # Set equal dim factor (we do not need status display here)
            "mode": PushButtonModes.LATCH,
            "id": id
        })


####################################################################################################################


# Provides mapping of the kemper internal effect types to effect categories
class KemperEffectCategories: #(EffectCategoryProvider):

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
        Defaults.DEFAULT_LABEL_COLOR,                   # None
        Colors.ORANGE,                                  # Wah
        Colors.RED,                                     # Distortion
        Colors.BLUE,                                    # Comp
        Colors.BLUE,                                    # Gate
        Colors.GREEN,                                   # Space
        Colors.BLUE,                                    # Chorus
        Colors.PURPLE,                                  # Phaser/Flanger
        Colors.YELLOW,                                  # EQ
        Colors.RED,                                     # Booster
        Colors.PURPLE,                                  # Looper
        Colors.WHITE,                                   # Pitch
        Colors.GREEN,                                   # Dual
        Colors.GREEN,                                   # Delay
        Colors.GREEN,                                   # Reverb
    ]

    # Effect type display names. The order must match the enums for the effect types defined above!
    CATEGORY_NAMES = [
        "-",
        "Wah",
        "Dist",
        "Comp",
        "Gate",
        "Space",
        "Chorus",
        "Phaser",
        "EQ",
        "Boost",
        "Looper",
        "Pitch",
        "Dual",
        "Delay",
        "Reverb"
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


####################################################################################################################


# Kemper specific SysEx message with defaults which are valid most of the time
class KemperNRPNMessage(SystemExclusive):

    def __init__(
            self, 
            function_code,
            address_page,
            address_number,
            manufacturer_id = NRPN_MANUFACTURER_ID, 
            product_type = NRPN_PRODUCT_TYPE,
            device_id = NRPN_DEVICE_ID_OMNI
        ):

        # Adafruit SystemExclusive
        super().__init__(
            manufacturer_id,                 # [0x00, 0x20, 0x33]
            [
                product_type,                # 0x02 (Player), 0x00 (Profiler)
                device_id,                   # 0x7f (omni) or manually set via parameter
                function_code,               # Selects the function, for example 0x41 for requesting a single parameter
                NRPN_INSTANCE,               # 0x00
                address_page,                # Controller MSB (address page)
                address_number               # Controller LSB (address number of parameter)
            ]
        )
        
# Kemper specific SysEx message for extended parameters 
class KemperNRPNExtendedMessage(SystemExclusive):
    
    def __init__(
            self, 
            function_code,
            controller,     # Must be a list
            manufacturer_id = NRPN_MANUFACTURER_ID, 
            product_type = NRPN_PRODUCT_TYPE,
            device_id = NRPN_DEVICE_ID_OMNI
        ):

        # Adafruit SystemExclusive
        super().__init__(
            manufacturer_id,                 # [0x00, 0x20, 0x33]
            [
                product_type,                # 0x02 (Player), 0x00 (Profiler)
                device_id,                   # 0x7f (omni) or manually set via parameter
                function_code,               # Selects the function, for example 0x41 for requesting a single parameter
                NRPN_INSTANCE                # 0x00                
            ] + controller
        )

####################################################################################################################


# Implements setting values and parsing request responses
class KemperMidiValueProvider: #(ClientValueProvider):

    # Parameter types (used internally in mappings)
    PARAMETER_TYPE_NUMERIC = 0   # Default, also used for on/off
    PARAMETER_TYPE_STRING = 1

    # Helper to convert values in range [0..1] to the NRPN value range of [0..16383]
    @staticmethod
    def NRPN_VALUE(value):
        return int(16383 * value)

    # Must parse the incoming MIDI message and set it on the passed mapping.
    # If the response template does not match, must return False.
    # Must return True to notify the listeners of a value change.
    def parse(self, mapping, midi_message):
        # Compare manufacturer IDs
        if midi_message.manufacturer_id != mapping.response.manufacturer_id:
            return False
        
        # Check if the message belongs to the mapping. The following have to match:
        #   2: function code, 
        #   3: instance ID, 
        #   4: address page, 
        #   5: address nunber
        #
        # The first two values are ignored (the Kemper MIDI specification implies this would contain the product type
        # and device ID as for the request, however the device just sends two zeroes)
        if midi_message.data[2:6] != mapping.response.data[2:6]:
            return False
        
        # The values starting from index 6 are the value of the response.
        if mapping.type == self.PARAMETER_TYPE_STRING:
            # Take as string
            mapping.value = ''.join(chr(int(c)) for c in list(midi_message.data[6:-1]))
        else:
            # Decode 14-bit value to int
            mapping.value = midi_message.data[-2] * 128 + midi_message.data[-1]

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
            data[6] = int(floor(value / 128))
            data[7] = int(value % 128)

            mapping.set.data = bytes(data)
        

####################################################################################################################


# Defines some useful MIDI mappings
class KemperMappings:

    # Effect slot enable/disable
    @staticmethod
    def EFFECT_STATE(slot_id):
        return ClientParameterMapping(
            name = "Effect Status " + str(slot_id),
            set = ControlChange(
                KemperEffectSlot.CC_EFFECT_SLOT_ENABLE[slot_id], 
                0    # Dummy value, will be overridden
            ),
            request = KemperNRPNMessage(               
                NRPN_FUNCTION_REQUEST_SINGLE_PARAMETER, 
                KemperEffectSlot.NRPN_SLOT_ADDRESS_PAGE[slot_id],
                NRPN_EFFECT_PARAMETER_ADDRESS_STATE
            ),
            response = KemperNRPNMessage(
                NRPN_FUNCTION_RESPONSE_SINGLE_PARAMETER,
                KemperEffectSlot.NRPN_SLOT_ADDRESS_PAGE[slot_id],
                NRPN_EFFECT_PARAMETER_ADDRESS_STATE
            )
        )
    
    # Effect slot type (request only)
    @staticmethod
    def EFFECT_TYPE(slot_id):
        return ClientParameterMapping(
            name = "Effect Type " + str(slot_id),
            request = KemperNRPNMessage(               
                NRPN_FUNCTION_REQUEST_SINGLE_PARAMETER, 
                KemperEffectSlot.NRPN_SLOT_ADDRESS_PAGE[slot_id],
                NRPN_EFFECT_PARAMETER_ADDRESS_TYPE
            ),
            response = KemperNRPNMessage(               
                NRPN_FUNCTION_RESPONSE_SINGLE_PARAMETER, 
                KemperEffectSlot.NRPN_SLOT_ADDRESS_PAGE[slot_id],
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
                KemperEffectSlot.NRPN_SLOT_ADDRESS_PAGE[slot_id],
                NRPN_EFFECT_PARAMETER_ADDRESS_ROTARY_SPEED
            ),
            request = KemperNRPNMessage(               
                NRPN_FUNCTION_REQUEST_SINGLE_PARAMETER, 
                KemperEffectSlot.NRPN_SLOT_ADDRESS_PAGE[slot_id],
                NRPN_EFFECT_PARAMETER_ADDRESS_ROTARY_SPEED
            ),
            response = KemperNRPNMessage(
                NRPN_FUNCTION_RESPONSE_SINGLE_PARAMETER,
                KemperEffectSlot.NRPN_SLOT_ADDRESS_PAGE[slot_id],
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
                KemperEffectSlot.NRPN_FREEZE_SLOT_PARAMETER_ADDRESSES[slot_id]
            ),
            request = KemperNRPNMessage(               
                NRPN_FUNCTION_REQUEST_SINGLE_PARAMETER, 
                NRPN_ADDRESS_PAGE_FREEZE,
                KemperEffectSlot.NRPN_FREEZE_SLOT_PARAMETER_ADDRESSES[slot_id]
            ),
            response = KemperNRPNMessage(               
                NRPN_FUNCTION_RESPONSE_SINGLE_PARAMETER, 
                NRPN_ADDRESS_PAGE_FREEZE,
                KemperEffectSlot.NRPN_FREEZE_SLOT_PARAMETER_ADDRESSES[slot_id]
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
        type = KemperMidiValueProvider.PARAMETER_TYPE_STRING
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
        type = KemperMidiValueProvider.PARAMETER_TYPE_STRING
    )

    # Switch tuner mode on/off (no receive possible when not in bidirectional mode)
    TUNER_MODE_STATE = ClientParameterMapping(
        name = "Tuner Mode",
        set = ControlChange(
            CC_TUNER_MODE, 
            0    # Dummy value, will be overridden
        ),
        response = KemperNRPNMessage(
            0x01,
            0x7f,
            0x7e
        )
    )

    # Tuner note (only sent in bidirectional mode)
    TUNER_NOTE = ClientParameterMapping(
        name = "Tuner Note",
        response = KemperNRPNMessage(
            0x01,
            0x7d,
            0x54
        )
    )

    # Tuner deviance from "in tune" (only sent in bidirectional mode)
    TUNER_DEVIANCE = ClientParameterMapping(
        name = "Tuner Deviance",
        response = KemperNRPNMessage(
            0x01,
            0x7c,
            0x0f
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
        type = KemperMidiValueProvider.PARAMETER_TYPE_STRING
    )

    # Amp on/off
    AMP_STATE = ClientParameterMapping(
        name = "Amp Status",
        set = KemperNRPNMessage(
            NRPN_FUNCTION_SET_SINGLE_PARAMETER, 
            NRPN_ADDRESS_PAGE_AMP,
            NRPN_AMP_PARAMETER_STATE
        ),
        request = KemperNRPNMessage(
            NRPN_FUNCTION_REQUEST_SINGLE_PARAMETER,
            NRPN_ADDRESS_PAGE_AMP,
            NRPN_AMP_PARAMETER_STATE
        ),
        response = KemperNRPNMessage(
            NRPN_FUNCTION_RESPONSE_SINGLE_PARAMETER,
            NRPN_ADDRESS_PAGE_AMP,
            NRPN_AMP_PARAMETER_STATE
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
        type = KemperMidiValueProvider.PARAMETER_TYPE_STRING
    )
    
    # Cab on/off
    CABINET_STATE = ClientParameterMapping(
        name = "Cab Status",
        set = KemperNRPNMessage(
            NRPN_FUNCTION_SET_SINGLE_PARAMETER, 
            NRPN_ADDRESS_PAGE_CABINET,
            NRPN_CABINET_PARAMETER_STATE
        ),
        request = KemperNRPNMessage(
            NRPN_FUNCTION_REQUEST_SINGLE_PARAMETER,
            NRPN_ADDRESS_PAGE_CABINET,
            NRPN_CABINET_PARAMETER_STATE
        ),
        response = KemperNRPNMessage(
            NRPN_FUNCTION_RESPONSE_SINGLE_PARAMETER,
            NRPN_ADDRESS_PAGE_CABINET,
            NRPN_CABINET_PARAMETER_STATE
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

    # Used for state sensing in bidirection communication
    BIDIRECTIONAL_SENSING = ClientParameterMapping(
        response = KemperNRPNExtendedMessage(
            0x7e,
            [
                0x7f
            ]
        )
    ) 
    

####################################################################################################################


PARAMETER_SET_2 = [
    KemperMappings.EFFECT_TYPE(KemperEffectSlot.EFFECT_SLOT_ID_A),
    KemperMappings.EFFECT_STATE(KemperEffectSlot.EFFECT_SLOT_ID_A),

    KemperMappings.EFFECT_TYPE(KemperEffectSlot.EFFECT_SLOT_ID_B),
    KemperMappings.EFFECT_STATE(KemperEffectSlot.EFFECT_SLOT_ID_B),

    KemperMappings.EFFECT_TYPE(KemperEffectSlot.EFFECT_SLOT_ID_C),
    KemperMappings.EFFECT_STATE(KemperEffectSlot.EFFECT_SLOT_ID_C),

    KemperMappings.EFFECT_TYPE(KemperEffectSlot.EFFECT_SLOT_ID_D),
    KemperMappings.EFFECT_STATE(KemperEffectSlot.EFFECT_SLOT_ID_D),

    KemperMappings.EFFECT_TYPE(KemperEffectSlot.EFFECT_SLOT_ID_X),
    KemperMappings.EFFECT_STATE(KemperEffectSlot.EFFECT_SLOT_ID_X),

    KemperMappings.EFFECT_TYPE(KemperEffectSlot.EFFECT_SLOT_ID_MOD),
    KemperMappings.EFFECT_STATE(KemperEffectSlot.EFFECT_SLOT_ID_MOD),

    KemperMappings.RIG_NAME,

    KemperMappings.TUNER_MODE_STATE,
    KemperMappings.TUNER_NOTE,
    KemperMappings.TUNER_DEVIANCE         
]

SELECTED_PARAMETER_SET_ID = 0x02
SELECTED_PARAMETER_SET = PARAMETER_SET_2


# Implements the internal Kemper bidirectional communication protocol
class KemperBidirectionalProtocol: #(BidirectionalProtocol):
    
    STATE_OFFLINE = 10   # No commmunication initiated
    STATE_RUNNING = 20   # Bidirectional communication established

    def __init__(self, time_lease_seconds):
        self.state = self.STATE_OFFLINE
        self._time_lease_encoded = self._encode_time_lease(time_lease_seconds)

        # This is the reponse template for the status sensing message the Profiler sends every
        # about 500ms.
        self._mapping_sense = KemperMappings.BIDIRECTIONAL_SENSING

        # Re-send the beacon after half of the lease time have passed
        self.resend_period = PeriodCounter(time_lease_seconds * 1000 * 0.5)

        # Period for initial beacons (those shall not be sent too often)
        self.init_period = PeriodCounter(5000)

        # Period after which communication will be regarded as broken when no sensing message comes in
        # (the device sends this roughly every 500ms so we wait 1.5 seconds which should be sufficient)
        self.sensing_period = PeriodCounter(1500)
        self.sensing_period.reset()

        self.debug = False   # This is set by the BidirectionalClient constructor
        self._count_input_messages = 0
        self._count_relevant_messages = 0
        
    # Called before usage, with a midi handler.
    def init(self, midi):
        self._midi = midi  

    # Must return (boolean) if the passed mapping is handled in the bidirectional protocol
    def is_bidirectional(self, mapping):
        return mapping in SELECTED_PARAMETER_SET

    # Must return a color representation for the current state
    def get_color(self):
        return Colors.GREEN if self.state == self.STATE_RUNNING else Colors.RED
 
    # Must return (boolean) if the passed mapping should feed back the set value immediately
    # without waiting for a midi message.
    def feedback_value(self, mapping):
        return self.is_bidirectional(mapping)

    # Initialize the communication and keeps it alive when time lease exceeds
    def update(self):
        if self.state == self.STATE_OFFLINE:
            if self.init_period.exceeded:
                if self.debug:
                    self._print("Initialize communication")

                self._send_beacon(
                    init = True
                )                        

        elif self.state == self.STATE_RUNNING:
            if self.sensing_period.exceeded:
                self.state = self.STATE_OFFLINE

                if self.debug:
                    self._print("Lost connection")

                self.resend_period.reset()

            if self.resend_period.exceeded:
                if self.debug:
                    self._print("Send keep-alive message")

                self._send_beacon()

    # Receive sensing messages and re-init (with init = 1 again) when they stop appearing for longer then 1 second
    def receive(self, midi_message):
        if self.debug:
            self._count_input_messages += 1

        if not isinstance(midi_message, SystemExclusive):
            return
               
        # Compare manufacturer IDs
        if midi_message.manufacturer_id != self._mapping_sense.response.manufacturer_id:
            return False
        
        if self.debug:
            self._count_relevant_messages += 1

        # Check if the message belongs to the status sense mapping. The following have to match:
        #   2: function code, (0x7e)
        #   3: instance ID,   (0x00)
        #   4: address page   (0x7f)
        #
        # The first two values are ignored (the Kemper MIDI specification implies this would contain the product type
        # and device ID as for the request, however the device just sends two zeroes)
        if midi_message.data[2:5] != self._mapping_sense.response.data[2:5]:
            return False
        
        #if self.debug:
        #    self._print("Received sensing message, communication is alive")
        
        if self.state != self.STATE_RUNNING:
            self.resend_period.reset()
            
            if self.debug:
               self._print("Connection established")

        self.state = self.STATE_RUNNING

        self.sensing_period.reset()

    # Send beacon for bidirection communication
    def _send_beacon(self, init = False):
        self._midi.send(
            KemperNRPNExtendedMessage(
                0x7e,
                [
                    0x40,
                    SELECTED_PARAMETER_SET_ID,
                    self._get_flags(
                        init = init,
                        tunemode = True
                    ),
                    self._time_lease_encoded
                ]
            )
        )

    # Encode time lease (this is done in 2 second steps for the Kemper)
    def _encode_time_lease(self, time_lease_seconds):
        return int(time_lease_seconds / 2)

    # Generates the flags byte.
    def _get_flags(self, init = False, sysex = True, echo = False, nofe = False, noctr = False, tunemode = False):
        i = 1 if init else 0
        s = 1 if sysex else 0
        e = 1 if echo else 0
        n = 1 if nofe else 0
        c = 1 if noctr else 0
        t = 1 if tunemode else 0

        return 0x00 | (i << 0) | (s << 1) | (e << 2) | (n << 3) | (c << 4) | (t << 5)

    def _print(self, msg):
        Tools.print("Bidirectional (" + Tools.formatted_timestamp() + "): " + msg + " (Received " + repr(self._count_relevant_messages) + " / " + repr(self._count_input_messages) + ")")
        self._count_input_messages = 0
        self._count_relevant_messages = 0
