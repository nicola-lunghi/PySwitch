from math import floor
from micropython import const

from adafruit_midi.control_change import ControlChange
from adafruit_midi.system_exclusive import SystemExclusive
from adafruit_midi.program_change import ProgramChange

from pyswitch.misc import Colors, PeriodCounter, DEFAULT_SWITCH_COLOR, DEFAULT_LABEL_COLOR, formatted_timestamp, do_print, PYSWITCH_VERSION
from pyswitch.controller.actions.actions import ResetDisplaysAction, PushButtonAction
from pyswitch.controller.actions.callbacks import BinaryParameterCallback, DEFAULT_LED_BRIGHTNESS_OFF, Callback, EffectEnableCallback
from pyswitch.controller.Client import ClientParameterMapping
from pyswitch.ui.elements import TunerDisplay


####################################################################################################################

# Definitions of devices
NRPN_PRODUCT_TYPE_PROFILER = const(0x00)                     # Kemper Profiler
NRPN_PRODUCT_TYPE_PROFILER_PLAYER = const(0x02)              # Kemper Profiler Player

# This defines which type of device to control
NRPN_PRODUCT_TYPE = NRPN_PRODUCT_TYPE_PROFILER_PLAYER

# Defines how many rigs one bank has
NUM_RIGS_PER_BANK = 5

####################################################################################################################

# ControlChange Addresses
CC_TUNER_MODE = const(31)
CC_BANK_INCREASE = const(48)
CC_BANK_DECREASE = const(49)
CC_RIG_SELECT = const(50)       # This selects slot 1 of the current bank. The slots 2-5 can be addressed by adding (n-1) to the value.
CC_BANK_PRESELECT = const(47)
CC_TAP_TEMPO = const(30)
CC_ROTARY_SPEED = const(33)     # 1 = Fast, 0 = Slow
CC_MORPH_PEDAL = const(11)
CC_MORPH_BUTTON = const(80)     # Also includes ride/fall times
CC_RIG_INDEX_PART_1 = const(32) # The second part will be sent as program change.

CC_EFFECT_BUTTON_I = const(75)  # II to IV are consecutive from this: 76, 77, 78

CC_VALUE_BANK_CHANGE = const(0)

# Basic values for all NRPN messages
NRPN_MANUFACTURER_ID = [0x00, 0x20, 0x33]       # Kemper manufacturer ID
NRPN_DEVICE_ID_OMNI = const(0x7f)               # Omni (all devices, only supported mode)
NRPN_INSTANCE = const(0x00)                     # Instance ID for NRPN. The profiler only supports instance 0.

# NRPN Adress pages
NRPN_ADDRESS_PAGE_STRINGS = const(0x00)
NRPN_ADDRESS_PAGE_RIG_PARAMETERS = const(0x04)
NRPN_ADDRESS_PAGE_FREEZE = const(0x7d)
NRPN_ADDRESS_PAGE_AMP = const(0x0a)
NRPN_ADDRESS_PAGE_CABINET = const(0x0c)

# NRPN Function codes
NRPN_FUNCTION_REQUEST_SINGLE_PARAMETER = const(0x41)
NRPN_FUNCTION_REQUEST_STRING_PARAMETER = const(0x43)
NRPN_FUNCTION_REQUEST_EXT_STRING_PARAMETER = const(0x47)

NRPN_FUNCTION_RESPONSE_SINGLE_PARAMETER = const(0x01)
NRPN_FUNCTION_RESPONSE_STRING_PARAMETER = const(0x03)

NRPN_FUNCTION_SET_SINGLE_PARAMETER = const(0x01)

# NRPN parameters for effect slots
NRPN_EFFECT_PARAMETER_ADDRESS_TYPE = const(0x00) 
NRPN_EFFECT_PARAMETER_ADDRESS_STATE = const(0x03)
NRPN_EFFECT_PARAMETER_ADDRESS_MIX = const(0x04)
NRPN_EFFECT_PARAMETER_ADDRESS_ROTARY_SPEED = const(0x1e)  # 30
NRPN_EFFECT_PARAMETER_ADDRESS_MIX2 = const(0x36)  # 54
NRPN_EFFECT_PARAMETER_ADDRESS_MIX_DLY_REV = const(0x45)  # 69
# ... add further parameters here

# Rig parameters (page 0x04)
NRPN_RIG_PARAMETER_VOLUME = const(0x01)
# ... add further parameters here

# Amp parameters (page 0x0a)
NRPN_AMP_PARAMETER_STATE = const(0x02)

# Cab parameters (page 0x0c)
NRPN_CABINET_PARAMETER_STATE = const(0x02)

# NRPN String parameters
NRPN_STRING_PARAMETER_ID_RIG_NAME = const(0x01)
NRPN_STRING_PARAMETER_ID_RIG_DATE = const(0x03)
NRPN_STRING_PARAMETER_ID_AMP_NAME = const(0x10)
NRPN_STRING_PARAMETER_ID_CABINET_NAME = const(0x20)

# Generally used NRPN values
NRPN_PARAMETER_OFF = const(0)
NRPN_PARAMETER_ON = const(1)

def NRPN_VALUE(value):
    return int(16383 * value)


####################################################################################################################

# All defined actions here have one parameter in common: A display definition (see definitions.py)
# which assigns a display label to the action (optional: If omitted, no visual feedback is given 
# on the display).
class KemperActionDefinitions: 

    # Binary parameters (for all binary parameter mappings which support 0/1 values for on/off)
    @staticmethod
    def BINARY_SWITCH(mapping, 
                      display = None, 
                      text = "", 
                      mode = PushButtonAction.HOLD_MOMENTARY, 
                      color = Colors.WHITE, 
                      id = False, 
                      use_leds = True, 
                      enable_callback = None,
                      value_on = 1,
                      value_off = 0,
        ):
        return PushButtonAction({
            "callback": BinaryParameterCallback(
                mapping = mapping,
                text = text,
                color = color,
                value_enable = value_on,
                value_disable = value_off,
                comparison_mode = BinaryParameterCallback.GREATER_EQUAL
            ),
            "mode": mode,
            "display": display,
            "id": id,
            "useSwitchLeds": use_leds,
            "enableCallback": enable_callback
        })

    ## Special functions ####################################################################################################

    # Switch an effect slot on / off
    @staticmethod
    def EFFECT_STATE(slot_id, 
                     display = None, 
                     mode = PushButtonAction.HOLD_MOMENTARY, 
                     id = False, 
                     use_leds = True, 
                     enable_callback = None
        ):
        return PushButtonAction({
            "callback": KemperEffectEnableCallback(slot_id),
            "mode": mode,
            "display": display,
            "id": id,
            "useSwitchLeds": use_leds,
            "enableCallback": enable_callback,
        })

    # Switch tuner mode on / off
    @staticmethod
    def TUNER_MODE(display = None, mode = PushButtonAction.HOLD_MOMENTARY, color = DEFAULT_SWITCH_COLOR, id = False, use_leds = True, enable_callback = None):
        return PushButtonAction({
            "callback": BinaryParameterCallback(
                mapping = KemperMappings.TUNER_MODE_STATE(),
                text = "Tuner",
                color = color,
                comparison_mode = BinaryParameterCallback.EQUAL,
            ),
            "mode": mode,   
            "display": display,            
            "id": id,
            "useSwitchLeds": use_leds,
            "enableCallback": enable_callback
        })

    # Tap tempo 
    @staticmethod
    def TAP_TEMPO(display = None, color = Colors.DARK_GREEN, id = False, use_leds = True, enable_callback = None):
        return PushButtonAction({
            "callback": BinaryParameterCallback(
                mapping = KemperMappings.TAP_TEMPO(),
                text = "Tap",
                color = color
            ),
            "mode": PushButtonAction.MOMENTARY,
            "display": display,
            "id": id,
            "useSwitchLeds": use_leds,
            "enableCallback": enable_callback
        })
    
    # Show tempo (visual feedback, will be enabled for short time every beat)
    @staticmethod
    def SHOW_TEMPO(display = None, color = Colors.LIGHT_GREEN, text = "Tempo", id = False, use_leds = True, enable_callback = None):
        return PushButtonAction({
            "callback": BinaryParameterCallback(
                mapping = KemperMappings.TEMPO_DISPLAY(),
                text = text,
                color = color
            ),
            "display": display,
            "id": id,
            "useSwitchLeds": use_leds,
            "enableCallback": enable_callback
        })
    
    # Effect Button I-IIII (set only). num must be a number (1 to 4).
    @staticmethod
    def EFFECT_BUTTON(num, text = None, display = None, color = Colors.LIGHT_GREEN, id = False, use_leds = True, enable_callback = None):
        if not text:
            if num == 1:
                text = "FX I"
            elif num == 2:
                text = "FX II"
            elif num == 3:
                text = "FX III"
            elif num == 4:
                text = "FX IIII"

        return PushButtonAction({
            "callback": BinaryParameterCallback(
                mapping = KemperMappings.EFFECT_BUTTON(num),
                text = text,
                color = color
            ),
            "mode": PushButtonAction.LATCH,
            "display": display,
            "id": id,
            "useSwitchLeds": use_leds,
            "enableCallback": enable_callback
        })
    
    # Morph button (faded change of morph state) No state feedback possible!
    #
    # NOTE: The Kemper MIDI Documentation differs from real behaviour here: The 
    # device changes state on every 0/1 value sequence instead of accepting 0/1 for on/off!
    # Even if you just send 1, it does not work: You have to send 0, then 1 to have the state change.
    def MORPH_BUTTON(display = None, color = Colors.LIGHT_GREEN, text = "Morph", id = False, use_leds = True, enable_callback = None):
        return PushButtonAction({
            "callback": BinaryParameterCallback(
                mapping = KemperMappings.MORPH_BUTTON(),
                text = text,
                color = color,
                value_enable = [0, 1],
            ),
            "mode": PushButtonAction.ONE_SHOT,            
            "useSwitchLeds": use_leds,
            "display": display,
            "id": id,
            "enableCallback": enable_callback
        })

    ## Rig specific ##########################################################################################################

    # Volume boost function, based on setting rig volume to a certain boost value. To 
    # make sense, all rig volumes have to be zero in your rigs! You can then set the
    # boost rig volume by passing a value in range [0..1] (corresponding to the range of the
    # rig volume paramneter: 0.5 is 0dB, 0.75 is +6dB, 1.0 is +12dB)
    @staticmethod
    def RIG_VOLUME_BOOST(boost_volume, 
                         display = None, 
                         mode = PushButtonAction.HOLD_MOMENTARY, 
                         color = Colors.PINK, 
                         id = False, 
                         use_leds = True, 
                         text = "RigBoost", 
                         remember_off_value = True, 
                         enable_callback = None
        ):
        return PushButtonAction({
            "callback": BinaryParameterCallback(
                mapping = KemperMappings.RIG_VOLUME(),
                text = text,
                color = color,
                value_enable = NRPN_VALUE(boost_volume),
                value_disable = NRPN_VALUE(0.5) if not remember_off_value else "auto",    # 0.5 = 0dB
            ),
            "mode": mode,
            "display": display,
            "id": id,
            "useSwitchLeds": use_leds,
            "enableCallback": enable_callback
        })

    # Used to reset the screen areas which show rig info details directly after rig changes (if you dont use this, 
    # you get no visual feedback on the device that a new rig is coming up)
    @staticmethod
    def RESET_RIG_INFO_DISPLAYS(id = False, enable_callback = None):
        return ResetDisplaysAction({
            "resetSwitches": True,
            "ignoreOwnSwitch": True,
            "resetDisplayAreas": True,
            "id": id,
            "enableCallback": enable_callback
        })

    ## Change Rig/Bank ############################################################################################################

    # Next bank (keeps rig index)
    @staticmethod
    def BANK_UP(display = None, color = Colors.WHITE, text = "Bank up", id = False, use_leds = True, enable_callback = None):
        return PushButtonAction({
            "callback": BinaryParameterCallback(
                mapping = KemperMappings.NEXT_BANK(),
                text = text,
                color = color,
                value_enable = CC_VALUE_BANK_CHANGE
            ),
            "mode": PushButtonAction.ONE_SHOT,
            "display": display,
            "id": id,
            "useSwitchLeds": use_leds,
            "enableCallback": enable_callback
        })
    
    # Previous bank (keeps rig index)
    @staticmethod
    def BANK_DOWN(display = None, color = Colors.WHITE, text = "Bank dn", id = False, use_leds = True, enable_callback = None):
        return PushButtonAction({
            "callback": BinaryParameterCallback(
                mapping = KemperMappings.PREVIOUS_BANK(),
                text = text,
                color = color,
                value_enable = CC_VALUE_BANK_CHANGE
            ),
            "mode": PushButtonAction.ONE_SHOT,
            "display": display,
            "id": id,
            "useSwitchLeds": use_leds,
            "enableCallback": enable_callback
        })
    
    # Selects a specific rig, or toggles between two rigs (if rig_off is also provided) in
    # the current bank. Rigs are indexed starting from one, range: [1..5].
    # Optionally, banks can be switched too in the same logic using bank and bank_off.
    @staticmethod
    def RIG_SELECT(rig, 
                   rig_off = None, 
                   bank = None, 
                   bank_off = None, 
                   display = None, 
                   color = Colors.YELLOW, 
                   id = False, 
                   use_leds = True, 
                   enable_callback = None
        ):
        
        # Mappings and values: Start with a configuration for rig_off == None and bank(_off) = None.
        mapping = KemperMappings.RIG_SELECT(rig - 1)
        mapping_disable = mapping

        value_enable = NRPN_PARAMETER_ON
        value_disable = value_enable

        # Bank for main rig
        if bank != None:
            mapping = KemperMappings.BANK_AND_RIG_SELECT(rig - 1)
            if rig_off == None:
                mapping_disable = mapping
            
            value_enable = [bank - 1, 1]
            value_disable = [bank - 1, 1]
            
        # Alternate rig (the rig selected when the switch state is False)
        if rig_off != None:
            # Use a different mapping for disabling
            mapping_disable = KemperMappings.RIG_SELECT(rig_off - 1)

        # Bank for alternate rig
        if bank_off != None:
            if rig_off == None:
                raise Exception() #"RIG_SELECT: If bank_off is set, you must also provide rig_off.")
            
            mapping_disable = KemperMappings.BANK_AND_RIG_SELECT(rig_off - 1)
            value_disable = [bank_off - 1, 1]

        # Callback implementation for Rig Select, showing bank colors and rig/bank info
        class RigSelectDisplayCallback(BinaryParameterCallback):
            # Bank colors
            BANK_COLORS = [
                Colors.BLUE,
                Colors.YELLOW,
                Colors.RED,
                Colors.TURQUOISE,
                Colors.PURPLE
            ]

            def __init__(self):
                super().__init__(
                    mapping = mapping,
                    mapping_disable = mapping_disable,
                    color = color,
                    value_enable = value_enable,
                    value_disable = value_disable,
                    comparison_mode = self.NO_STATE_CHANGE
                )

            def update_displays(self, action):
                if mapping.value == None:
                    # Fallback to default behaviour
                    super().update_displays(action)
                    return
                
                # Calculate bank and rig numbers in range [0...]
                bank = int(mapping.value / NUM_RIGS_PER_BANK)
                rig = mapping.value % NUM_RIGS_PER_BANK

                # Label text
                action.label.text = "Rig " + repr(bank + 1) + "-" + repr(rig + 1)

                # Bank color
                bank_color = self.BANK_COLORS[bank % len(self.BANK_COLORS)]
                action.label.back_color = bank_color

                action.switch_color = bank_color
                action.switch_brightness = DEFAULT_LED_BRIGHTNESS_OFF
    
        # Finally we can create the action definition ;)
        return PushButtonAction({
            "display": display,
            "mode": PushButtonAction.LATCH,
            "id": id,
            "useSwitchLeds": use_leds,
            "callback": RigSelectDisplayCallback(),
            "enableCallback": enable_callback
        })


####################################################################################################################


# Used for effect enable/disable ParameterAction
class KemperEffectEnableCallback(EffectEnableCallback):

    # Effect types enum (used internally, also for indexing colors, so be sure these are always a row from 0 to n)
    CATEGORY_WAH = const(1)
    CATEGORY_DISTORTION = const(2)
    CATEGORY_COMPRESSOR = const(3)
    CATEGORY_NOISE_GATE = const(4)
    CATEGORY_SPACE = const(5)
    CATEGORY_CHORUS = const(6)
    CATEGORY_PHASER_FLANGER = const(7)
    CATEGORY_EQUALIZER = const(8)
    CATEGORY_BOOSTER = const(9)
    CATEGORY_LOOPER = const(10)
    CATEGORY_PITCH = const(11)
    CATEGORY_DUAL = const(12)
    CATEGORY_DELAY = const(13)
    CATEGORY_REVERB = const(14)

    # Effect colors. The order must match the enums for the effect types defined above!
    CATEGORY_COLORS = (
        DEFAULT_LABEL_COLOR,                            # None
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
    )

    # Effect type display names. The order must match the enums for the effect types defined above!
    CATEGORY_NAMES = (
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
    )

    def __init__(self, slot_id):
        super().__init__(
            mapping_state = KemperMappings.EFFECT_STATE(slot_id),
            mapping_type = KemperMappings.EFFECT_TYPE(slot_id)
        )
    
    # Must return the effect category for a mapping value
    def get_effect_category(self, kpp_effect_type):
        # NOTE: The ranges are defined by Kemper with a lot of unused numbers, so the borders between types
        # could need to be adjusted with future Kemper firmware updates!
        if (kpp_effect_type == 0):
            return self.CATEGORY_NONE
        elif (0 < kpp_effect_type and kpp_effect_type <= 14):
            return self.CATEGORY_WAH
        elif (14 < kpp_effect_type and kpp_effect_type <= 45):
            return self.CATEGORY_DISTORTION
        elif (45 < kpp_effect_type and kpp_effect_type <= 55):
            return self.CATEGORY_COMPRESSOR
        elif (55 < kpp_effect_type and kpp_effect_type <= 60):
            return self.CATEGORY_NOISE_GATE       
        elif (60 < kpp_effect_type and kpp_effect_type <= 64):
            return self.CATEGORY_SPACE            
        elif (64 < kpp_effect_type and kpp_effect_type <= 80):
            return self.CATEGORY_CHORUS
        elif (80 < kpp_effect_type and kpp_effect_type <= 95):
            return self.CATEGORY_PHASER_FLANGER
        elif (95 < kpp_effect_type and kpp_effect_type <= 110):
            return self.CATEGORY_EQUALIZER
        elif (110 < kpp_effect_type and kpp_effect_type <= 120):
            return self.CATEGORY_BOOSTER
        elif (120 < kpp_effect_type and kpp_effect_type <= 125):
            return self.CATEGORY_LOOPER
        elif (125 < kpp_effect_type and kpp_effect_type <= 135):
            return self.CATEGORY_PITCH
        elif (135 < kpp_effect_type and kpp_effect_type <= 143):
            return self.CATEGORY_DUAL
        elif (143 < kpp_effect_type and kpp_effect_type <= 170):
            return self.CATEGORY_DELAY
        else:
            return self.CATEGORY_REVERB
        
    # Must return the color for a category    
    def get_effect_category_color(self, category):
        return self.CATEGORY_COLORS[category]

    # Must return the text to show for a category    
    def get_effect_category_text(self, category):
        return self.CATEGORY_NAMES[category]
         

####################################################################################################################


# Callback for DisplayLabel to show the rig name
class KemperRigNameCallback(Callback):
    DEFAULT_TEXT = "Kemper Control " + PYSWITCH_VERSION

    def __init__(self):
        Callback.__init__(self)
        self._mapping = KemperMappings.RIG_NAME()
        self.mappings = [self._mapping]

    def update_label(self, label):
        label.text = self._mapping.value if self._mapping.value else self.DEFAULT_TEXT


####################################################################################################################


# Splash Callback for on-demand Tuner display. Pass your default display root element as default splash,
# and a genuine tuner display will be used when the tuner is activated. You can also define your own tuner
# display optionally.
class TunerDisplayCallback(Callback):
    def __init__(self, splash_default, splash_tuner = None):
        Callback.__init__(self)

        self._mapping = KemperMappings.TUNER_MODE_STATE()
        self.mappings = [self._mapping]
        
        self._splash_tuner = splash_tuner
        self._splash_default = splash_default

        if not self._splash_tuner:
            self._splash_tuner = TunerDisplay(
                mapping_note = KemperMappings.TUNER_NOTE(),
                mapping_deviance = KemperMappings.TUNER_DEVIANCE(),
                
                bounds = self._splash_default.bounds,
                
                scale = 3,
                layout = {
                    "font": "/fonts/PTSans-NarrowBold-40.pcf"
                }
            )

    def get_root(self):
        if self._mapping.value != 1:
            return self._splash_default
        else:
            return self._splash_tuner


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


# Kemper Effect slot IDs, MIDI addresses and display properties
class KemperEffectSlot:
    
    # IDs for the available effect slots
    EFFECT_SLOT_ID_A = const(0)
    EFFECT_SLOT_ID_B = const(1)
    EFFECT_SLOT_ID_C = const(2)
    EFFECT_SLOT_ID_D = const(3)
    
    EFFECT_SLOT_ID_X = const(4)
    EFFECT_SLOT_ID_MOD = const(5)
    EFFECT_SLOT_ID_DLY = const(6)
    EFFECT_SLOT_ID_REV = const(7)

    # CC Address for Effect Slot enable/disable. Order has to match the one defined above!
    CC_EFFECT_SLOT_ENABLE = (
        const(17),    # Slot A
        const(18),    # Slot B
        const(19),    # Slot C
        const(20),    # Slot D

        const(22),    # Slot X
        const(24),    # Slot MOD        
        const(27),    # Slot DLY (with Spillover)        
        const(29)     # Slot REV (with Spillover)
    )

    # Slot address pages. Order has to match the one defined above!
    NRPN_SLOT_ADDRESS_PAGE = (
        const(0x32),   # Slot A
        const(0x33),   # Slot B
        const(0x34),   # Slot C
        const(0x35),   # Slot D

        const(0x38),   # Slot X
        const(0x3a),   # Slot MOD
        const(0x3c),   # Slot DLY
        const(0x3d)    # Slot REV
    )    

    # Freeze parameter addresses on page 0x7d (Looper and Delay Freeze) for all slots. 
    # Order has to match the one defined above!
    NRPN_FREEZE_SLOT_PARAMETER_ADDRESSES = [
        const(0x6b),   # Slot A
        const(0x6c),   # Slot B
        const(0x6d),   # Slot C
        const(0x6e),   # Slot D

        const(0x6f),   # Slot X
        const(0x71),   # Slot MOD
        const(0x72),   # Slot DLY
        const(0x73)    # Slot REV
    ]    


####################################################################################################################


# Implements setting values and parsing request responses
class KemperParameterMapping(ClientParameterMapping):

    # Parameter types (used internally in mappings)
    PARAMETER_TYPE_NUMERIC = const(0)   # Default, also used for on/off
    PARAMETER_TYPE_STRING = const(1)

    def __init__(self, name = "", set = None, request = None, response = None, value = None, type = 0):
        super().__init__(name = name, set = set, request = request, response = response, value = value)
        self.type = type

    # Must parse the incoming MIDI message and set its value on the mapping.
    # If the response template does not match, must return False, and
    # vice versa must return True to notify the listeners of a value change.
    def parse(self, midi_message):     
        result = self.parse_against(midi_message, self.response)
        if result != None:
            self.value = result
            return True
        
        return False

    # Parse a message against a response message
    def parse_against(self, midi_message, response):     
        # SysEx (NRPN) Messages
        if isinstance(midi_message, SystemExclusive):
            if not isinstance(response, SystemExclusive):
                return None
                     
            # Compare manufacturer IDs
            if midi_message.manufacturer_id != response.manufacturer_id:
                return None
            
            # Check if the message belongs to the mapping. The following have to match:
            #   2: function code, 
            #   3: instance ID, 
            #   4: address page, 
            #   5: address nunber
            #
            # The first two values are ignored (the Kemper MIDI specification implies this would contain the product type
            # and device ID as for the request, however the device just sends two zeroes)
            if midi_message.data[2:6] != response.data[2:6]:
                return None
            
            # The values starting from index 6 are the value of the response.
            if self.type == self.PARAMETER_TYPE_STRING:
                # Take as string
                return ''.join(chr(int(c)) for c in list(midi_message.data[6:-1]))
            else:
                # Decode 14-bit value to int
                return midi_message.data[-2] * 128 + midi_message.data[-1]

        # CC Messages
        elif isinstance(midi_message, ControlChange):
            if not isinstance(response, ControlChange):
                return None
            
            if midi_message.control == response.control:
                return midi_message.value

        # PC Messages
        elif isinstance(midi_message, ProgramChange):
            if not isinstance(response, ProgramChange):
                return None
            
            return midi_message.patch

        # MIDI Clock (disabled in favor of the custom beat message the kemper sends. See mapping TEMPO_DISPLAY)
        #elif isinstance(midi_message, MidiClockMessage):
        #    self._count_clock += 1

        #    if self._count_clock >= 24:
        #        self._count_clock = 0

        #    if self._count_clock >= 12:
        #        mapping.value = 1
        #    else:
        #        mapping.value = 0    

        #    return True
        
        # MIDI Clock start
        #elif isinstance(midi_message, Start):
        #    self._count_clock = 0

        #    mapping.value = 1

        #    return True

        return None
    
    # Must set the passed value(s) on the SET message(s) of the mapping.
    def set_value(self, value):
        if isinstance(self.set, list):
            for i in range(len(self.set)):
                self._set_value(self.set[i], value[i])
        else:
            self._set_value(self.set, value)

    def _set_value(self, midi_message, value):
        if isinstance(midi_message, ControlChange):
            # Set value directly (CC takes int values)            
            midi_message.value = value

        elif isinstance(midi_message, SystemExclusive):            
            # Fill up message to appropriate length for the specification
            data = list(midi_message.data)
            while len(data) < 8:
                data.append(0)
            
            # Set value as 14 bit
            data[6] = int(floor(value / 128))
            data[7] = int(value % 128)

            midi_message.data = bytes(data)
        

####################################################################################################################


# Parser for two-part messages: The result value will be 128 * value1 + value2, 
# notified when the second message arrives.
class KemperTwoPartParameterMapping(KemperParameterMapping):

    def __init__(self, name = "", set = None, request = None, response = None, value = None, type = 0):
        super().__init__(name = name, set = set, request = request, response = response, value = value, type = type)

        self._value_1 = None
    
    # Must parse the incoming MIDI message and set its value on the mapping.
    # If the response template does not match, must return False, and
    # vice versa must return True to notify the listeners of a value change.
    def parse(self, midi_message): 
        value_1 = self.parse_against(midi_message, self.response[0])
        if value_1 != None:
            self._value_1 = value_1
            return True
        
        value_2 = self.parse_against(midi_message, self.response[1])

        if value_2 != None and self._value_1 != None:
            self.value = 128 * self._value_1 + value_2
            self._value_1 = None
            return True
        
        return False
            
    # Returns if the mapping has finished receiving a result. Per default,
    # this returns True which is valid for mappings with one response.
    def result_finished(self):
        return (self._value_1 == None)


####################################################################################################################


# Defines some useful MIDI mappings
class KemperMappings:

    # Effect slot enable/disable
    @staticmethod
    def EFFECT_STATE(slot_id):
        return KemperParameterMapping(
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
        return KemperParameterMapping(
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
        return KemperParameterMapping(
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
        return KemperParameterMapping(
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
    
    def EFFECT_MIX(slot_id):
        return KemperParameterMapping(
            name = "Mix " + str(slot_id),
            set = KemperNRPNMessage(
                NRPN_FUNCTION_SET_SINGLE_PARAMETER, 
                KemperEffectSlot.NRPN_SLOT_ADDRESS_PAGE[slot_id],
                NRPN_EFFECT_PARAMETER_ADDRESS_MIX_DLY_REV
            ),
            request = KemperNRPNMessage(               
                NRPN_FUNCTION_REQUEST_SINGLE_PARAMETER, 
                KemperEffectSlot.NRPN_SLOT_ADDRESS_PAGE[slot_id],
                NRPN_EFFECT_PARAMETER_ADDRESS_MIX_DLY_REV
            ),
            response = KemperNRPNMessage(               
                NRPN_FUNCTION_RESPONSE_SINGLE_PARAMETER, 
                KemperEffectSlot.NRPN_SLOT_ADDRESS_PAGE[slot_id],
                NRPN_EFFECT_PARAMETER_ADDRESS_MIX_DLY_REV
            )
        )

    # Effect Button I-IIII (set only). num must be a number (1 to 4).
    def EFFECT_BUTTON(num): 
        return KemperParameterMapping(
            name = "Effect Button " + repr(num),
            set = ControlChange(
                CC_EFFECT_BUTTON_I + (num - 1),
                0
            )
        )

    # Rig name (request only)
    def RIG_NAME(): 
        return KemperParameterMapping(
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
            type = KemperParameterMapping.PARAMETER_TYPE_STRING
        )

    # Rig date (request only)
    def RIG_DATE(): 
        return KemperParameterMapping(
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
            type = KemperParameterMapping.PARAMETER_TYPE_STRING
        )

    # Switch tuner mode on/off (no receive possible when not in bidirectional mode)
    def TUNER_MODE_STATE(): 
        return KemperParameterMapping(
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
    def TUNER_NOTE(): 
        return KemperParameterMapping(
            name = "Tuner Note",
            response = KemperNRPNMessage(
                0x01,
                0x7d,
                0x54
            )
        )

    # Tuner deviance from "in tune" (only sent in bidirectional mode)
    def TUNER_DEVIANCE(): 
        return KemperParameterMapping(
            name = "Tuner Deviance",
            response = KemperNRPNMessage(
                0x01,
                0x7c,
                0x0f
            )
        )

    # Switch tuner mode on/off (no receive possible!)
    def TAP_TEMPO(): 
        return KemperParameterMapping(
            name = "Tap Tempo",
            set = ControlChange(
                CC_TAP_TEMPO, 
                0    # Dummy value, will be overridden
            )
        )

    def MORPH_BUTTON(): 
        return KemperParameterMapping(
            set = [
                ControlChange(CC_MORPH_BUTTON, 0),
                ControlChange(CC_MORPH_BUTTON, 1)
            ]
        )

    def MORPH_PEDAL(): 
        return KemperParameterMapping(
            set = ControlChange(CC_MORPH_PEDAL, 0)
        )

    # Rig volume
    def RIG_VOLUME(): 
        return KemperParameterMapping(
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
    def AMP_NAME(): 
        return KemperParameterMapping(
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
            type = KemperParameterMapping.PARAMETER_TYPE_STRING
        )

    # Amp on/off
    def AMP_STATE(): 
        return KemperParameterMapping(
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
    def CABINET_NAME(): 
        return KemperParameterMapping(
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
            type = KemperParameterMapping.PARAMETER_TYPE_STRING
        )
    
    # Cab on/off
    def CABINET_STATE(): 
        return KemperParameterMapping(
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

    def NEXT_BANK(): 
        return KemperParameterMapping(
            name = "Next Bank",
            set = ControlChange(
                CC_BANK_INCREASE,
                0    # Dummy value, will be overridden
            )
        )

    def PREVIOUS_BANK():
        return KemperParameterMapping(
            name = "Prev Bank",
            set = ControlChange(
                CC_BANK_DECREASE,
                0    # Dummy value, will be overridden
            )
        )

    # Selects a rig of the current bank. Rig index must be in range [0..4]
    def RIG_SELECT(rig):
        return KemperTwoPartParameterMapping(
            name = "Rig Select",
            set = ControlChange(
                CC_RIG_SELECT + rig,
                0    # Dummy value, will be overridden
            ),

            response = [
                ControlChange(
                    CC_RIG_INDEX_PART_1,
                    0    # Dummy value, will be ignored
                ),
                ProgramChange(
                    0    # Dummy value, will be ignored
                )
            ]
        )
    
    # Selects a rig of a specific bank. Rig index must be in range [0..4]
    def BANK_AND_RIG_SELECT(rig):
        return KemperTwoPartParameterMapping(
            name = "Rig+Bank",
            set = [
                ControlChange(
                    CC_BANK_PRESELECT,
                    0    # Dummy value, will be overridden
                ),
                ControlChange(
                    CC_RIG_SELECT + rig,
                    0    # Dummy value, will be overridden
                )
            ],

            response = [
                ControlChange(
                    CC_RIG_INDEX_PART_1,
                    0    # Dummy value, will be ignored
                ),
                ProgramChange(
                    0    # Dummy value, will be ignored
                )
            ]
        )

    # Used for state sensing in bidirection communication
    def BIDIRECTIONAL_SENSING():
        return KemperParameterMapping(
            name = "Sense",
            response = KemperNRPNExtendedMessage(
                0x7e,
                [
                    0x7f
                ]
            )
        ) 

    # MIDI Clock message, sent 24x every beat
    #MIDI_CLOCK = KemperParameterMapping(
    #    name = "Clock",
    #    response = MidiClockMessage()
    #)
    
    #MIDI_CLOCK_START = KemperParameterMapping(
    #    name = "Start",
    #    response = Start()
    #)

    def TEMPO_DISPLAY():
        return KemperParameterMapping(
            name = "Tempo",
            response = KemperNRPNExtendedMessage(
                0x01,
                [
                    0x7c,
                    0x00,
                    0x00
                ]
            )
        )
    

####################################################################################################################


_PARAMETER_SET_2 = [
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

    KemperMappings.RIG_NAME(),

    KemperMappings.TUNER_MODE_STATE(),
    KemperMappings.TUNER_NOTE(),
    KemperMappings.TUNER_DEVIANCE()
]

_SELECTED_PARAMETER_SET_ID = const(0x02)
_SELECTED_PARAMETER_SET = _PARAMETER_SET_2


# Implements the internal Kemper bidirectional communication protocol
class KemperBidirectionalProtocol: #(BidirectionalProtocol):
    
    _STATE_OFFLINE = 10   # No commmunication initiated
    _STATE_RUNNING = 20   # Bidirectional communication established

    def __init__(self, time_lease_seconds):
        self.state = self._STATE_OFFLINE
        self._time_lease_encoded = self._encode_time_lease(time_lease_seconds)

        # This is the reponse template for the status sensing message the Profiler sends every
        # about 500ms.
        self._mapping_sense = KemperMappings.BIDIRECTIONAL_SENSING()

        # Re-send the beacon after half of the lease time have passed
        self.resend_period = PeriodCounter(time_lease_seconds * 1000 * 0.5)

        # Period for initial beacons (those shall not be sent too often)
        self.init_period = PeriodCounter(5000)

        # Period after which communication will be regarded as broken when no sensing message comes in
        # (the device sends this roughly every 500ms so we wait 1.5 seconds which should be sufficient)
        self.sensing_period = PeriodCounter(1500)
        self.sensing_period.reset()

        self.debug = False   # This is set by the BidirectionalClient constructor
        self._count_relevant_messages = 0
        self._has_been_running = False
        
    # Called before usage, with a midi handler.
    def init(self, midi, client):
        self._midi = midi  
        self._client = client

    # Must return (boolean) if the passed mapping is handled in the bidirectional protocol
    def is_bidirectional(self, mapping):
        return mapping in _SELECTED_PARAMETER_SET

    # Must return a color representation for the current state
    def get_color(self):
        return Colors.GREEN if self.state == self._STATE_RUNNING else Colors.RED
 
    # Must return (boolean) if the passed mapping should feed back the set value immediately
    # without waiting for a midi message.
    def feedback_value(self, mapping):
        return self.is_bidirectional(mapping)

    # Initialize the communication and keeps it alive when time lease exceeds
    def update(self):
        if self.state == self._STATE_OFFLINE:
            if self.init_period.exceeded:
                if self.debug:
                    self._print("Initialize")

                if self._has_been_running:
                    self._client.notify_connection_lost()                    

                self._send_beacon(
                    init = True
                )

        elif self.state == self._STATE_RUNNING:
            if self.sensing_period.exceeded:
                self.state = self._STATE_OFFLINE

                if self.debug:
                    self._print("Lost connection")                

            elif self.resend_period.exceeded:
                if self.debug:
                    self._print("Send keep-alive message")

                self._send_beacon()

    # Receive sensing messages and re-init (with init = 1 again) when they stop appearing for longer then 1 second
    def receive(self, midi_message):
        if not isinstance(midi_message, SystemExclusive):
            return False
               
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
        
        if self.state != self._STATE_RUNNING:
            self.resend_period.reset()
            
            if self.debug:
               self._print("Connection established")

            self._has_been_running = True
            self.state = self._STATE_RUNNING

        self.sensing_period.reset()

        return True

    # Send beacon for bidirection communication
    def _send_beacon(self, init = False):
        self._midi.send(
            KemperNRPNExtendedMessage(
                0x7e,
                [
                    0x40,
                    _SELECTED_PARAMETER_SET_ID,
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
        do_print("Bidirectional (" + formatted_timestamp() + "): " + msg + " (Received " + repr(self._count_relevant_messages) + ")")
        self._count_relevant_messages = 0
