#################################################################################################################################
# 
# Device configuration for the KemperStomp script.
#
#################################################################################################################################
 
import board
from .definitions import Ports, Actions, PushButtonModes, DisplayAreas, Colors
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
                    # Action type. This determines what the action does, and which configuration options it needs.
                    "type": Actions.BINARY_PARAMETER,

                    # MIDI mapping for the BINARY_PARAMETER Action.
                    "mapping": KemperMappings.MAPPING_EFFECT_SLOT_ON_OFF(KemperMidi.EFFECT_SLOT_ID_A),

                    # On/off values for the BINARY_PARAMETER Action.
                    "valueEnabled": KemperMidi.NRPN_PARAMETER_ON,
                    "valueDisabled": KemperMidi.NRPN_PARAMETER_OFF,

                    # If this is defined (it is optional!), the action will show stuff on the display. Valid
                    # for all action types which want to make use of the display, but optional.
                    "display": {
                        # Defines the area to put the action label. The available display areas (header, footer) 
                        # will be populated in the order the actions are defined in this file.
                        "area": DisplayAreas.HEADER,

                        # The index inside the above defined display area (only applicable if the display area
                        # supports multiple slots, as the header and footer do)). Keep all indices of one area 
                        # in a row starting from 0 (not 1!), or you will get empty areas!
                        "index": 0
                    }
                }
            ]
        },
        {
            "assignment": Ports.PA_MIDICAPTAIN_NANO_SWITCH_2,
            "actions": [
                {
                    "type": Actions.BINARY_PARAMETER,                    
                    "mapping": KemperMappings.MAPPING_EFFECT_SLOT_ON_OFF(KemperMidi.EFFECT_SLOT_ID_B),
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
                    "type": Actions.BINARY_PARAMETER,                    
                    "mapping": KemperMappings.MAPPING_EFFECT_SLOT_ON_OFF(KemperMidi.EFFECT_SLOT_ID_B),
                    "display": {
                        "area": DisplayAreas.FOOTER,
                        "index": 0
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
                        "index": 1
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
        # Layout for the info area (rig name) label
        "infoAreaLayout": {
            "font": "/fonts/PTSans-NarrowBold-40.pcf",     # Font path (mandatory)
            "lineSpacing": 0.8,                            # Line spacing (optional) default: 1
            "maxTextWidth": 220,                           # Maximum text width in pixels (for example: 220 at a display width of 240), optional
            "textColor": (215, 255, 255),                  # Text color (optional, default is automatic detection by back color)
            "backColor": (20, 50, 30),                     # Back color (optional, default is no background at all)

            # Text initially shown in the center area (where the rig name goes later on).
            "text": "Kemper\nEffects Slot Mode",
        },

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
        "on": 0.2,
        "off": 0.005,
        "notAssigned": 0
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

    # Debug mode. Shows verbose console output. You can listen to that on the serial REPL port via USB on your computer,
    # see https://learn.adafruit.com/welcome-to-circuitpython/advanced-serial-console-on-mac-and-linux 
    "debug": True,

    "debugDisplay": False,       # Show verbose messages from the display user interface
    "debugActions": False,       # Show verbose messages from actions
    "debugSwitches": False,      # Show verbose output for switches (color, brightness) or a switches actions are triggered
    "debugKemper": True,         # Show all requests and responses to/from the Kemper Profiler
    "debugMidi": False,          # Debug Adafruit MIDI controller. Normally it is sufficient and more readable to  
                                 # enable "debugKemper" instead, which also shows the MIDI messages sent and received.

    # Set this to True to boot into explore mode. This mode listens to all GPIO pins available
    # and outputs the ID of the last pushed one, and also rotates through all available NeoPixels. 
    # Use this to detect the switch assignments on unknown devices.
    "exploreMode": False
}
