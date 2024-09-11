#################################################################################################################################
# 
# Configuration script for the KemperStomp script.
#
#################################################################################################################################
 
from kemperstomp_ports import Ports

# Device Configuration. Change this to program your device as needed. Use the constants defined in 
# kemperstomp.ports.py to assign behaviour to the switches, as well as some general options.
Config = {
    # Defines the available switches (order is not regarded). Use the constants above to assign 
    # the switches to the correct GPIO ports and LED pixels.
    "switches": [
        {
            "assignment": Ports.PA_MIDICAPTAIN_NANO_SWITCH_1
        },
        {
            "assignment": Ports.PA_MIDICAPTAIN_NANO_SWITCH_2
        },
        {
            "assignment": Ports.PA_MIDICAPTAIN_NANO_SWITCH_3
        },
        {
            "assignment": Ports.PA_MIDICAPTAIN_NANO_SWITCH_4
        }
    ],

    # Parameters of the user interface
    "userInterface": {
        # Height of the four effect unit label areas (pixels, default: 40)
        "effectLabelHeight": 40,

        # Text initially shown in the center area (where the rig name goes later on)
        "initialInfoText": "Kemper\nEffects Slot Mode",

        # Maximum text width in pixels (default: 220)
        "maxTextWidth": 220,

        # Maximum text width in characters (default: 14)
        "maxTextWidthCharacters": 14,
    },

    # Selects the MIDI channel to use [1..16]
    "midiChannel": 1,

    # MIDI buffer size (default: 60)
    "midiBufferSize": 60,
}



