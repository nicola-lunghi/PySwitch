##############################################################################################################################################
# 
# Device configuration for the KemperStomp script.
#
##############################################################################################################################################
 
import board

from .definitions import Ports, ActionTypes, PushButtonModes, Colors, FootSwitchDefaults, DisplayDefaults, ProcessingConfig
from .display import DisplayAreas
from .mappings import KemperMappings
from .actions import ActionDefinitions
from .kemper import KemperMidi, KemperMidiValueProvider

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
                ActionDefinitions.EFFECT_ON_OFF(
                    slot_id = KemperMidi.EFFECT_SLOT_ID_A,
                    display = {
                        "id": DisplayAreas.HEADER,
                        "index": 0
                    }
                )                
            ]
        },
        {
            "assignment": Ports.PA_MIDICAPTAIN_NANO_SWITCH_2,
            "actions": [
                ActionDefinitions.EFFECT_ON_OFF(
                    slot_id = KemperMidi.EFFECT_SLOT_ID_B,
                    display = {
                        "id": DisplayAreas.HEADER,
                        "index": 1
                    },
                    mode = PushButtonModes.MOMENTARY
                )    
            ]
        },
        {
            "assignment": Ports.PA_MIDICAPTAIN_NANO_SWITCH_A,
            "actions": [
                ActionDefinitions.AMP_ON_OFF(
                    display = {
                        "id": DisplayAreas.FOOTER,
                        "index": 0
                    },
                    color = (Colors.WHITE, Colors.YELLOW, Colors.LIGHT_GREEN)  
                )
            ]
        },
        {
            "assignment": Ports.PA_MIDICAPTAIN_NANO_SWITCH_B,
            "actions": [
                ActionDefinitions.RESET_RIG_INFO_DISPLAYS,
                ActionDefinitions.RIG_SELECT(
                    rig = 1,
                    bank = 1,

                    rig_off = 5,
                    bank_off = 3,

                    display = {
                        "id": DisplayAreas.FOOTER,
                        "index": 1
                    }   
                )
            ]
        }
    ],

    # Defines which data to show where on the TFT display (optional). The display layout is defined in
    # display.py. Here, you create mappings between the display areas and parameter values of the Kemper,
    # which will automatically be updated regularily.
    #
    # Don't put too much in here, as the performance could suffer!
    "displays": [
        # Rig name
        { 
            "mapping": KemperMappings.RIG_NAME,
            "depends": KemperMappings.RIG_DATE,  # Only update this when the rig date changed (optional)
            "display": {
                "id": DisplayAreas.RIG_NAME
            },
            "textOffline": "Kemper Profiler (offline)",
            "textReset": "Loading Rig..."
        },

        # Amp name
        { 
            "mapping": KemperMappings.AMP_NAME,
            "depends": KemperMappings.RIG_DATE,  # Only update this when the rig date changed (optional)
            "display": {
                "id": DisplayAreas.DETAIL
            }
        }
    ],

    # Optional: Override brightness settings for all switch LEDs. Range: [0..1]
    "ledBrightness": {
        "on": FootSwitchDefaults.DEFAULT_BRIGHTNESS_ON,
        "off": FootSwitchDefaults.DEFAULT_BRIGHTNESS_OFF,
    },

    # Optional: Factor used to dim the colors in the display (not the switches!) Range [0..1]
    "displayDimFactorOn": DisplayDefaults.DEFAULT_SLOT_DIM_FACTOR_ON,
    "displayDimFactorOff": DisplayDefaults.DEFAULT_SLOT_DIM_FACTOR_OFF,

## MIDI and other Options ################################################################################################################

    # Max. milliseconds until a request is being terminated and it is
    # assumed that the Kemper device is offline. Optional, default is KemperDefinitions.DEFAULT_MAX_REQUEST_LIFETIME_MILLIS.
    "maxRequestLifetimeMillis": ProcessingConfig.DEFAULT_MAX_REQUEST_LIFETIME_MILLIS,

    # Selects the MIDI channel to use [1..16]
    "midiChannel": 1,

    # MIDI buffer size (60 is a good value)
    "midiBufferSize": 60,

    # Update interval, for updating the rig date (which triggers all other data to update when changed) (milliseconds)
    # and other displays if assigned. 200 is a good value.
    "updateInterval": 200,

    # Port at which the NeoPixel is addressed (example: board.GP7 for most (?) PaintAudio MIDI Captain devices)
    "neoPixelPort": board.GP7,

    # Value provider which is responsible for setting values on MIDI messages for value changes, and parse MIDI messages
    # when an answer to a value request is received.
    "valueProvider": KemperMidiValueProvider(),

## Development Options ###################################################################################################################

    # Shows an area with statistics (for debugging)
    "showFrameStats": False,

    # Debug mode, optional. Shows verbose console output. You can listen to that on the serial port via USB on your computer,
    # see https://learn.adafruit.com/welcome-to-circuitpython/advanced-serial-console-on-mac-and-linux 
    "debug": False,

    "debugUserInterfaceStructure": False,    # Show UI structure after init 
    "debugDisplay": False,                   # Show verbose messages from the display elements. Optional.
    "debugActions": False,                   # Show verbose messages from actions. Optional.
    "debugSwitches": False,                  # Show verbose output for switches (color, brightness) or a switches 
                                             # actions are triggered. Optional.
    "debugParameters": False,                # Show messages from the global parameter controller
    "debugClient": False,                    # Show all requests and responses to/from the Kemper Profiler. Optional.
    #"clientDebugMapping": KemperMappings.NEXT_BANK, # Optional, if set the kemper classes will only output messages related to
                                             # the specified mapping.
    "debugClientRawMidi": False,             # Debug raw kemper MIDI messages. Only regarded whe "debugKemper" is enabled, too.
    "debugMidi": False,                      # Debug Adafruit MIDI controller. Normally it is sufficient and more readable 
                                             # to enable "debugKemperRawMidi" instead, which also shows the MIDI messages sent
                                             # and received. Optional.

    # Set this to True to boot into explore mode. This mode listens to all GPIO pins available
    # and outputs the ID of the last pushed one, and also rotates through all available NeoPixels. 
    # Use this to detect the switch assignments on unknown devices. Optional.
    "exploreMode": False
}
