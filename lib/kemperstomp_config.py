#################################################################################################################################
# 
# Configuration script for the KemperStomp script.
#
#################################################################################################################################
 
import board
from kemperstomp_def import Ports, Actions, Slots

#################################################################################################################################

# Device Configuration. Change this to program your device as needed. Use the constants defined in 
# kemperstomp.ports.py to assign behaviour to the switches, as well as some general options.
Config = {
    # Defines the available switches (order is not regarded). Use the constants above to assign 
    # the switches to the correct GPIO ports and LED pixels.
    "switches": [
        {
            "assignment": Ports.PA_MIDICAPTAIN_NANO_SWITCH_1,
            "actions": [
                {
                    "type": Actions.EFFECT_ON_OFF,
                    "slot": Slots.EFFECT_SLOT_ID_DLY
                }
            ]
        },
        {
            "assignment": Ports.PA_MIDICAPTAIN_NANO_SWITCH_2,
            "actions": [
                {
                    "type": Actions.EFFECT_ON_OFF,
                    "slot": Slots.EFFECT_SLOT_ID_REV
                }
            ]
        },
        {
            "assignment": Ports.PA_MIDICAPTAIN_NANO_SWITCH_3,
            "actions": [
                {
                    "type": Actions.EFFECT_ON_OFF,
                    "slot": Slots.EFFECT_SLOT_ID_A
                }
            ]
        },
        {
            "assignment": Ports.PA_MIDICAPTAIN_NANO_SWITCH_4,
            "actions": [
                {
                    "type": Actions.REBOOT,   #Actions.EFFECT_ON_OFF,
                    "slot": Slots.EFFECT_SLOT_ID_B
                }
            ]
        }
    ],

    # Parameters of the user interface
    "userInterface": {
        # Height of the four effect unit label areas (pixels, default: 40)
        "effectLabelHeight": 40,

        # Text initially shown in the center area (where the rig name goes later on)
        "initialInfoText": "Kemper\nEffects Slot Mode",

        # Layout for the effect slot labels
        "effectSlotLayout": {
            # Font
            "font": "/fonts/H20.pcf",
        },

        # Layout for the info area (rig name) label
        "infoAreaLayout": {
            # Font 
            "font": "/fonts/PTSans-NarrowBold-40.pcf",

            # Line spacing
            "lineSpacing": 0.8,

            # Maximum text width in pixels (default: 220 at a display width of 240)
            "maxTextWidth": 220            
        },

        # Layout for the debug area (when switched on)
        "debugAreaLayout": {
            # Font
            "font": "/fonts/H20.pcf",
        },
    },

    # Brightness settings for all LEDs. Range: [0..1]
    "ledBrightness": {
        "on": 0.7,
        "off": 0.1,
        "notAssigned": 0
    },

    # Selects the MIDI channel to use [1..16]
    "midiChannel": 1,

    # MIDI buffer size (default: 60)
    "midiBufferSize": 60,

    # Port at which the NeoPixel is addressed
    "neoPixelPort": board.GP7,

    # Debug mode (shows stats on the user interface)
    "debug": True
}



