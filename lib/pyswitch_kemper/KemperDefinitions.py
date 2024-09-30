#################################################################################################################################
# 
# Global kemper configuration for the KemperStomp script: definitions of kemper MIDI addresses, effect categories and a defaulted
# SysEx message class to be used in mappings for convenience. The MIDI message composition/parsing is also implemented here.
#
#################################################################################################################################

from pyswitch.definitions import Colors

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

