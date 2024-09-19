#################################################################################################################################
# 
# Device configuration for the KemperStomp script.
#
#################################################################################################################################
 
import board
from .definitions import Ports, Actions, PushButtonModes, Colors, FootSwitchDefaults
from .display import DisplayAreas
from .mappings import KemperMidi, KemperMappings

Config = {

## Hardware Assignment ######################################################################################################

    # Defines the available switches (order is not relevant). Use the constants defined in kemperstomp_def.py to assign 
    # the switches to the correct GPIO ports and LED pixels on your device.
    "switches": [
        {
            # Selects which switch of your device you want to assign
            "assignment": Ports.PA_MIDICAPTAIN_NANO_SWITCH_1,

            # Defines the actions you want to happen on different events of the switch. You can 
            # define as many actions as you want, they will be executed in that order.
            "actions": [
                {
                    "type": Actions.EFFECT_ON_OFF,
                    "slot": KemperMidi.EFFECT_SLOT_ID_A,
                    "display": {
                        "area": DisplayAreas.HEADER,
                        "index": 0
                    }
                }
            ]
        },
        {
            "assignment": Ports.PA_MIDICAPTAIN_NANO_SWITCH_2,
            "actions": [
                {
                    "type": Actions.EFFECT_ON_OFF,
                    "slot": KemperMidi.EFFECT_SLOT_ID_B,
                    "display": {
                        "area": DisplayAreas.HEADER,
                        "index": 1
                    }
                }
            ]
        },
        {
            "assignment": Ports.PA_MIDICAPTAIN_NANO_SWITCH_A,
            "actions": [
                {
                    "type": Actions.REBOOT,
                    "display": {
                        "area": DisplayAreas.FOOTER,
                        "index": 0,
                        "text": "Reboot"
                    }
                }
            ]
        },
        {
            "assignment": Ports.PA_MIDICAPTAIN_NANO_SWITCH_B,
            "actions": [
                {
                    "type": Actions.BINARY_PARAMETER,
                    "mapping": KemperMappings.TUNER_MODE_ON_OFF,                    
                    "display": {
                        "area": DisplayAreas.FOOTER,
                        "index": 1,
                        "text": "Tuner"
                    }
                }
            ]
        }
    ],

    # Port at which the NeoPixel is addressed (example: board.GP7 for most PaintAudio MIDI Captain devices)
    "neoPixelPort": board.GP7,

## User Interface Parameters ################################################################################################

    # Parameters of the user interface
    "userInterface": {
        # Shows an area with statistics (for debugging)
        "showFrameStats": False,

        # Layout for the statistics area (only necessary when switched on)
        "statsAreaLayout": {
            "font": "/fonts/H20.pcf",
            "backColor": (20, 20, 70),
            "textColor": (255, 255, 0),
        },

        # Height of the statistics area (only necessary when switched on)
        "statsAreaHeight": 40
    },

    # Brightness settings for all switch LEDs. Range: [0..1]
    "ledBrightness": {
        "on": FootSwitchDefaults.DEFAULT_BRIGHTNESS_ON,
        "off": FootSwitchDefaults.DEFAULT_BRIGHTNESS_OFF,
        "notAssigned": FootSwitchDefaults.DEFAULT_BRIGHTNESS_NOT_ASSIGNED
    },

    # Factor used to dim the colors in the display (not the switches!) Range [0..1]
    "displayDimFactor": 0.2,

## MIDI and other Options #################################################################################################

    # Selects the MIDI channel to use [1..16]
    "midiChannel": 1,

    # MIDI buffer size (default: 60)
    "midiBufferSize": 60,

    # Update interval, for updating rig info (milliseconds)
    "updateInterval": 1000, #50,

## Development Options #####################################################################################################+

    # Max. milliseconds until a request is being terminated and it is
    # assumed that the Kemper device is offline. Optional.
    "maxRequestLifetimeMillis": 2000,

    # Debug mode, optional. Shows verbose console output. You can listen to that on the serial port via USB on your computer,
    # see https://learn.adafruit.com/welcome-to-circuitpython/advanced-serial-console-on-mac-and-linux 
    "debug": False,

    "debugDisplay": False,        # Show verbose messages from the display user interface. Optional.
    "debugActions": False,        # Show verbose messages from actions. Optional.
    "debugSwitches": False,       # Show verbose output for switches (color, brightness) or a switches 
                                  # actions are triggered. Optional.
    "debugKemper": False,         # Show all requests and responses to/from the Kemper Profiler. Optional.
    "debugKemperRawMidi": False,  # Debug raw kemper MIDI messages. Only regarded whe "debugKemper" is enabled, too.
    "debugMidi": False,           # Debug Adafruit MIDI controller. Normally it is sufficient and more readable 
                                  # to enable "debugKemperRawMidi" instead, which also shows the MIDI messages sent
                                  # and received. Optional.

    # Set this to True to boot into explore mode. This mode listens to all GPIO pins available
    # and outputs the ID of the last pushed one, and also rotates through all available NeoPixels. 
    # Use this to detect the switch assignments on unknown devices. Optional.
    "exploreMode": False
}
