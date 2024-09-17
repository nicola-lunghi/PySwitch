from .KemperCommands import KemperCommands
from .KemperParameterParser import KemperParameterParser
from .KemperParameterRequests import KemperParameterRequests

from ...definitions import KemperDefinitions

# Provides all Kemper related functionality. This class itself only implements some type handling,
# the implementations themselves are located in the superclasses:
class Kemper(KemperCommands, KemperParameterRequests, KemperParameterParser):

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
        KemperCommands(midi_usb)
        KemperParameterRequests(midi_usb)

        self._midi_usb = midi_usb

    # Derives the effect type (enum of this class) from the effect type returned by the profiler.
    def get_effect_type(self, kpp_effect_type):
        # NOTE: The ranges are defined by Kemper with a lot of unised numbers, so the borders between types
        # could need to be adjusted with future Kemper firmware updates!
        if (kpp_effect_type == 0):
            return Kemper.TYPE_NONE
        elif (0 < kpp_effect_type and kpp_effect_type <= 14):
            return Kemper.TYPE_WAH
        elif (14 < kpp_effect_type and kpp_effect_type <= 45):
            return Kemper.TYPE_DISTORTION
        elif (45 < kpp_effect_type and kpp_effect_type <= 55):
            return Kemper.TYPE_COMPRESSOR
        elif (55 < kpp_effect_type and kpp_effect_type <= 60):
            return Kemper.TYPE_NOISE_GATE       
        elif (60 < kpp_effect_type and kpp_effect_type <= 64):
            return Kemper.TYPE_SPACE            
        elif (64 < kpp_effect_type and kpp_effect_type <= 80):
            return Kemper.TYPE_CHORUS
        elif (80 < kpp_effect_type and kpp_effect_type <= 95):
            return Kemper.TYPE_PHASERFLANGER
        elif (95 < kpp_effect_type and kpp_effect_type <= 110):
            return Kemper.TYPE_EQUALIZER
        elif (110 < kpp_effect_type and kpp_effect_type <= 120):
            return Kemper.TYPE_BOOSTER
        elif (120 < kpp_effect_type and kpp_effect_type <= 125):
            return Kemper.TYPE_LOOPER
        elif (125 < kpp_effect_type and kpp_effect_type <= 135):
            return Kemper.TYPE_PITCH
        elif (135 < kpp_effect_type and kpp_effect_type <= 143):
            return Kemper.TYPE_DUAL
        elif (143 < kpp_effect_type and kpp_effect_type <= 170):
            return Kemper.TYPE_DELAY
        else:
            return Kemper.TYPE_REVERB

