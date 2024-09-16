from adafruit_midi.control_change import ControlChange
from adafruit_midi.system_exclusive import SystemExclusive

from .KemperResponse import KemperResponse

from ...kemperstomp_def import KemperDefinitions, Slots


# Implements all Kemper Player related functionality 
# (MIDI messaging etc.)
class KemperProfilerPlayer:

    # Effect types enum (used internally, also for indexing colors, so be sure these are always a row from 0 to n)
    TYPE_NONE = 0
    TYPE_WAH = 1
    TYPE_DISTORTION = 2
    TYPE_COMPRESSOR = 3
    TYPE_NOISE_GATE = 4
    TYPE_SPACE = 5
    TYPE_CHORUS = 6
    TYPE_PHASER_FLANGER = 7
    TYPE_EQUALIZER = 8
    TYPE_BOOSTER = 9
    TYPE_LOOPER = 10
    TYPE_PITCH = 11
    TYPE_DUAL = 12
    TYPE_DELAY = 13
    TYPE_REVERB = 14

    # Effect colors. The order must match the enums for the effect types defined above!
    TYPE_COLORS = [
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
    TYPE_NAMES = [
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

    # Requires an USB driver instance
    def __init__(self, midi_usb):
        self.midi_usb = midi_usb

    # Derives the effect type (enum of this class) from the effect type returned by the profiler.
    def get_effect_type(self, kpp_effect_type):
        # NOTE: The ranges are defined by Kemper with a lot of unised numbers, so the borders between types
        # could need to be adjusted with future Kemper firmware updates!
        if (kpp_effect_type == 0):
            return KemperProfilerPlayer.TYPE_NONE
        elif (0 < kpp_effect_type and kpp_effect_type <= 14):
            return KemperProfilerPlayer.TYPE_WAH
        elif (14 < kpp_effect_type and kpp_effect_type <= 45):
            return KemperProfilerPlayer.TYPE_DISTORTION
        elif (45 < kpp_effect_type and kpp_effect_type <= 55):
            return KemperProfilerPlayer.TYPE_COMPRESSOR
        elif (55 < kpp_effect_type and kpp_effect_type <= 60):
            return KemperProfilerPlayer.TYPE_NOISE_GATE       
        elif (60 < kpp_effect_type and kpp_effect_type <= 64):
            return KemperProfilerPlayer.TYPE_SPACE            
        elif (64 < kpp_effect_type and kpp_effect_type <= 80):
            return KemperProfilerPlayer.TYPE_CHORUS
        elif (80 < kpp_effect_type and kpp_effect_type <= 95):
            return KemperProfilerPlayer.TYPE_PHASERFLANGER
        elif (95 < kpp_effect_type and kpp_effect_type <= 110):
            return KemperProfilerPlayer.TYPE_EQUALIZER
        elif (110 < kpp_effect_type and kpp_effect_type <= 120):
            return KemperProfilerPlayer.TYPE_BOOSTER
        elif (120 < kpp_effect_type and kpp_effect_type <= 125):
            return KemperProfilerPlayer.TYPE_LOOPER
        elif (125 < kpp_effect_type and kpp_effect_type <= 135):
            return KemperProfilerPlayer.TYPE_PITCH
        elif (135 < kpp_effect_type and kpp_effect_type <= 143):
            return KemperProfilerPlayer.TYPE_DUAL
        elif (143 < kpp_effect_type and kpp_effect_type <= 170):
            return KemperProfilerPlayer.TYPE_DELAY
        else:
            return KemperProfilerPlayer.TYPE_REVERB

    # Request all rig info (except date)
    def request_rig_info(self):
        self.request_effect_types()
        self.request_rig_name()
        self.request_effects_status()

    # Request rig name
    def request_rig_name(self):
        self.midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                           [0x02, 0x7f, 0x43, 0x00, 0x00, 0x01]))

    # Request rig creation date
    def request_rig_date(self):
        self.midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                           [0x02, 0x7f, 0x43, 0x00, 0x00, 0x03]))

    # Sets a slot enabled or disabled
    def set_slot_enabled(self, slot_id, enable):
        enable_int = 0
        if enable == True:
            enable_int = 1

        self.midi_usb.send(ControlChange(Slots.CC_EFFECT_SLOT_ENABLE[slot_id], enable_int))

    # Request types of effect for all slots
    def request_effect_types(self):
        self.request_effect_type(Slots.EFFECT_SLOT_ID_A)
        self.request_effect_type(Slots.EFFECT_SLOT_ID_B)
        self.request_effect_type(Slots.EFFECT_SLOT_ID_DLY)
        self.request_effect_type(Slots.EFFECT_SLOT_ID_REV)

    # Request the effect type of a specific slot
    def request_effect_type(self, slot_id):     
        self.request_single_parameter(
            Slots.SLOT_ADDRESS_PAGE[slot_id], 
            KemperDefinitions.PARAMETER_ADDRESS_EFFECT_TYPE
        )

    # Request effect status for all slots
    def request_effects_status(self):
        self.request_effect_status(Slots.EFFECT_SLOT_ID_A)
        self.request_effect_status(Slots.EFFECT_SLOT_ID_B)
        self.request_effect_status(Slots.EFFECT_SLOT_ID_DLY)
        self.request_effect_status(Slots.EFFECT_SLOT_ID_REV)

    # Request effect status for a specific slot
    def request_effect_status(self, slot_id):
        self.request_single_parameter(
            Slots.SLOT_ADDRESS_PAGE[slot_id], 
            KemperDefinitions.PARAMETER_ADDRESS_EFFECT_STATUS
        )

    def request_single_parameter(self, page, address):
        self.midi_usb.send(
            SystemExclusive(
                [
                    0x00, 
                    0x20, 
                    0x33
                ],
                [
                    0x02, 
                    0x7f, 
                    0x41, 
                    0x00, 
                    page,
                    address
                ]
            )
        )

    # Parse a response for the current rig name
    def parse_rig_name(self, midi_message):
        return self.parse_global_parameter(midi_message, KemperDefinitions.RESPONSE_PREFIX_RIG_NAME)
        
    # Parse a response for the current rig last changed date
    def parse_rig_date(self, midi_message):
        return self.parse_global_parameter(midi_message, KemperDefinitions.RESPONSE_PREFIX_RIG_DATE)

    # Parse a global parameter response
    def parse_global_parameter(self, midi_message, response_prefix):
        if not isinstance(midi_message, SystemExclusive):
            return None

        response = list(midi_message.data)
                
        if response[:6] != response_prefix:
            return None
        
        return KemperResponse(
            KemperDefinitions.RESPONSE_ID_GLOBAL_PARAMETER,
            ''.join(chr(int(c)) for c in response[6:-1])
        )

    # Parse a response for an effect type. Returns None if not relevant to the context.
    def parse_effect_type(self, midi_message, slot_id):
        return self.parse_effect_response(midi_message, slot_id, KemperDefinitions.RESPONSE_ID_EFFECT_TYPE)

    # Parse a response for an effect status. Returns None if not relevant to the context.
    def parse_effect_status(self, midi_message, slot_id):
        return self.parse_effect_response(midi_message, slot_id, KemperDefinitions.RESPONSE_ID_EFFECT_STATUS)

    # Parse a response for an effect parameter. Returns None if not relevant to the context.
    def parse_effect_response(self, midi_message, slot_id, response_type):
        if not isinstance(midi_message, SystemExclusive):
            return None

        response = list(midi_message.data)
                
        if response[:-3] != [0x00, 0x00, 0x01, 0x00, Slots.SLOT_ADDRESS_PAGE[slot_id]]:
            # Message does not belong to this slot
            return None

        if response[5] != response_type:
            # Message is the wrong response type
            return None

        if response[5] == KemperDefinitions.RESPONSE_ID_EFFECT_TYPE:
            # Response to an effect type request
            kpp_effect_type = response[-2] * 128 + response[-1]
            
            return KemperResponse(
                KemperDefinitions.RESPONSE_ID_EFFECT_TYPE,
                self.get_effect_type(kpp_effect_type)
            )
        
        elif response[5] == KemperDefinitions.RESPONSE_ID_EFFECT_STATUS:
            # Response to an effect status request
            if (response[-1] == KemperDefinitions.RESPONSE_ANSWER_STATUS_ON):
                # Effect on
                return KemperResponse(
                    KemperDefinitions.RESPONSE_ID_EFFECT_TYPE,
                    True
                )
            elif (response[-1] == KemperDefinitions.RESPONSE_ANSWER_STATUS_OFF):
                # Effect off
                return KemperResponse(
                    KemperDefinitions.RESPONSE_ID_EFFECT_TYPE,
                    False
                )