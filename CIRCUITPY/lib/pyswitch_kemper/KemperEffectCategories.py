#################################################################################################################################
# 
# Global kemper configuration for the KemperStomp script: definitions of kemper MIDI addresses, effect categories and a defaulted
# SysEx message class to be used in mappings for convenience. The MIDI message composition/parsing is also implemented here.
#
#################################################################################################################################

from pyswitch.core.controller.actions.EffectEnableAction import EffectCategoryProvider

from lib.pyswitch.core.misc.Colors import Colors
from lib.pyswitch.core.misc.Defaults import Defaults

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


