#from .KemperCommands import KemperCommands
#from .KemperParameterParser import KemperParameterParser
#from .KemperParameterRequests import KemperParameterRequests

from ...definitions import KemperDefinitions

# Provides mapping of the kemper internal effect types to effect categories
class KemperEffectCategories:

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

    # Derives the effect category from the effect type returned by the profiler.
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
            return KemperEffectCategories.CATEGORY_PHASERFLANGER
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
