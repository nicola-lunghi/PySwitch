##############################################################################################################################################
# 
# Device configuration for the KemperStomp script.
#
##############################################################################################################################################
 
import board

from .definitions import Ports, ActionTypes, PushButtonModes, Colors, FootSwitchDefaults, KemperDefinitions, KemperMidi
from .display import DisplayAreas
from .mappings import KemperMappings
from .actions import Actions

Config = {

## Hardware Assignment ########################################################################################################################

    # Defines the available switches (order is not relevant). Use the constants defined in kemperstomp_def.py to assign 
    # the switches to the correct GPIO ports and LED pixels on your device.
    "switches": [
        {
            # Selects which switch of your device you want to assign
            "assignment": Ports.PA_MIDICAPTAIN_NANO_SWITCH_1,

            # Defines the actions you want to happen on different events of the switch. You can 
            # define as many actions as you want, they will be executed in that order.
            "actions": [
                Actions.EFFECT_ON_OFF(
                    slot_id = KemperMidi.EFFECT_SLOT_ID_A,
                    display = {
                        "area": DisplayAreas.HEADER,
                        "index": 0
                    }
                )                
            ]
        },
        {
            "assignment": Ports.PA_MIDICAPTAIN_NANO_SWITCH_2,
            "actions": [
                Actions.EFFECT_ON_OFF(
                    slot_id = KemperMidi.EFFECT_SLOT_ID_REV,
                    display = {
                        "area": DisplayAreas.HEADER,
                        "index": 1
                    },
                    mode = PushButtonModes.MOMENTARY
                )    
            ]
        },
        {
            "assignment": Ports.PA_MIDICAPTAIN_NANO_SWITCH_A,
            "actions": [
                Actions.BANK_UP(
                    display =  {
                        "area": DisplayAreas.FOOTER,
                        "index": 0,
                        "text": "+Bank"
                    }   
                )
            ]
        },
        {
            "assignment": Ports.PA_MIDICAPTAIN_NANO_SWITCH_B,
            "actions": [
                Actions.BANK_DOWN(
                    display =  {
                        "area": DisplayAreas.FOOTER,
                        "index": 1,
                        "text": "-Bank"
                    }   
                )
            ]
        }
    ],

    # Defines which data to show where on the TFT display (optional)
    "displays": [
        # Rig name
        { 
            "mapping": KemperMappings.RIG_NAME,
            "depends": KemperMappings.RIG_DATE,  # Only update this when the rig date changed (optional)
            "display": {
                "area": DisplayAreas.RIG_NAME
            }
        },

        # Amp name
        { 
            "mapping": KemperMappings.AMP_NAME,
            "depends": KemperMappings.RIG_DATE,  # Only update this when the rig date changed (optional)
            "display": {
                "area": DisplayAreas.DETAIL
            }
        }
    ],

    # Optional: Override brightness settings for all switch LEDs. Range: [0..1]
    "ledBrightness": {
        "on": FootSwitchDefaults.DEFAULT_BRIGHTNESS_ON,
        "off": FootSwitchDefaults.DEFAULT_BRIGHTNESS_OFF,
    },

    # Optional: Factor used to dim the colors in the display (not the switches!) Range [0..1]
    "displayDimFactor": KemperDefinitions.DEFAULT_SLOT_DIM_FACTOR,

## MIDI and other Options ################################################################################################################

    # Max. milliseconds until a request is being terminated and it is
    # assumed that the Kemper device is offline. Optional, default is KemperDefinitions.DEFAULT_MAX_REQUEST_LIFETIME_MILLIS.
    "maxRequestLifetimeMillis": KemperDefinitions.DEFAULT_MAX_REQUEST_LIFETIME_MILLIS,

    # Selects the MIDI channel to use [1..16]
    "midiChannel": 1,

    # MIDI buffer size (60 is a good value)
    "midiBufferSize": 60,

    # Update interval, for updating the rig date (which triggers all other data to update when changed) (milliseconds)
    # and other displays if assigned. 200 is a good value.
    "updateInterval": 2000,

    # Port at which the NeoPixel is addressed (example: board.GP7 for most (?) PaintAudio MIDI Captain devices)
    "neoPixelPort": board.GP7,

## Development Options ###################################################################################################################

    # Shows an area with statistics (for debugging)
    "showFrameStats": True,

    # Debug mode, optional. Shows verbose console output. You can listen to that on the serial port via USB on your computer,
    # see https://learn.adafruit.com/welcome-to-circuitpython/advanced-serial-console-on-mac-and-linux 
    "debug": False,

    "debugDisplay": False,        # Show verbose messages from the display user interface. Optional.
    "debugActions": False,        # Show verbose messages from actions. Optional.
    "debugSwitches": False,       # Show verbose output for switches (color, brightness) or a switches 
                                  # actions are triggered. Optional.
    "debugParameters": False,     # Show messages from the global parameter controller
    "debugKemper": False,         # Show all requests and responses to/from the Kemper Profiler. Optional.
    #"kemperDebugMapping": KemperMappings.NEXT_BANK, # Optional, if set the kemper classes will only output messages related to
                                  # the specified mapping.
    "debugKemperRawMidi": False,  # Debug raw kemper MIDI messages. Only regarded whe "debugKemper" is enabled, too.
    "debugMidi": False,           # Debug Adafruit MIDI controller. Normally it is sufficient and more readable 
                                  # to enable "debugKemperRawMidi" instead, which also shows the MIDI messages sent
                                  # and received. Optional.

    # Set this to True to boot into explore mode. This mode listens to all GPIO pins available
    # and outputs the ID of the last pushed one, and also rotates through all available NeoPixels. 
    # Use this to detect the switch assignments on unknown devices. Optional.
    "exploreMode": False
}
