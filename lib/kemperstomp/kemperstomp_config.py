#################################################################################################################################
# 
# Configuration script for the KemperStomp script.
#
#################################################################################################################################
 
import board
from .kemperstomp_def import Ports, Actions, Slots, Colors

Config = {

## Hardware Assignment ######################################################################################################

    # Defines the available switches (order is not relevant). Use the constants defined in kemperstomp_def.py to assign 
    # the switches to the correct GPIO ports and LED pixels on your device.
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
                    "type": Actions.EFFECT_ON_OFF,
                    "slot": Slots.EFFECT_SLOT_ID_B
                }
            ]
        }
    ],

    # Port at which the NeoPixel is addressed (example: board.GP7 for most PaintAudio MIDI Captain devices)
    "neoPixelPort": board.GP7,

## User Interface Parameters ################################################################################################

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
        "on": 0.4,
        "off": 0.005,
        "notAssigned": 0
    },

## MIDI and other Options #################################################################################################

    # Selects the MIDI channel to use [1..16]
    "midiChannel": 1,

    # MIDI buffer size (default: 60)
    "midiBufferSize": 60,

    # Update interval, for updating rig info (seconds)
    "updateInterval": 0.05,

## Development Options #####################################################################################################+

    # Debug mode (shows verbose info)
    "debug": True,

    # Set this to True to boot into explore mode. This mode listens to all GPIO pins available
    # and outputs the ID of the last pushed one, and also rotates through all available NeoPixels. 
    # Use this to detect the switch assignments on unknown devices.
    "exploreMode": False,

    # Layout for the explore mode (when switched on)
    "exploreModeLayout": {
        # Font
        "font": "/fonts/PTSans-NarrowBold-40.pcf",

        # Maximum text width in pixels (default: 220 at a display width of 240)
        "maxTextWidth": 220,

        # Line spacing
        "lineSpacing": 0.8
    },
}
