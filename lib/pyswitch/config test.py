##############################################################################################################################################
# 
# Device configuration
#
##############################################################################################################################################
 
from .definitions import Colors, DisplayAreas, ActionTypes
from .defaults import FootSwitchDefaults
from .switches import Switches

from .core.controller.conditions.ParameterCondition import ParameterCondition, ParameterConditionModes
from .core.controller.conditions.PushButtonCondition import PushButtonCondition
from .core.controller.actions.base.PushButtonAction import PushButtonModes

from pyswitch_kemper.KemperMappings import KemperMappings
from pyswitch_kemper.KemperActionDefinitions import KemperActionDefinitions
from pyswitch_kemper.KemperMidi import KemperMidi
from pyswitch_kemper.KemperMidiValueProvider import KemperMidiValueProvider

from .ui.DisplayBounds import DisplayBounds
from .ui.elements.DisplayLabel import DisplayLabel
from .ui.elements.ParameterDisplayLabel import ParameterDisplayLabel
from .ui.elements.DisplaySplitContainer import DisplaySplitContainer
from .ui.elements.PerformanceIndicator import PerformanceIndicator

# Custom (local) display IDs. Just used locally here to reference header and footer display areas in the action definitions.
DISPLAY_HEADER = 10
DISPLAY_FOOTER = 20   

Config = {

## Hardware Assignment ########################################################################################################################

    # Defines the available switches (order is not relevant). Use the constants defined in kemperstomp_def.py to assign 
    # the switches to the correct GPIO ports and LED pixels on your device.
    "switches": [
        {
            # Selects which switch of your device you want to assign
            "assignment": Switches.PA_MIDICAPTAIN_NANO_SWITCH_1,

            # Defines the actions you want to happen on different events of the switch. You can 
            # define as many actions as you want, they will be executed in that order.
            # You can also use the Condition class to have different actions active depending
            # on another parameter.
            "actions": [
                ParameterCondition(
                    mapping = KemperMappings.RIG_VOLUME,
                    mode = ParameterConditionModes.MODE_GREATER_EQUAL,
                    ref_value = KemperMidi.NRPN_VALUE(0.5),

                    yes = [
                        KemperActionDefinitions.EFFECT_ON_OFF(
                            id = "sw1",
                            slot_id = KemperMidi.EFFECT_SLOT_ID_A,
                        ),
                        KemperActionDefinitions.EFFECT_ON_OFF(
                            slot_id = KemperMidi.EFFECT_SLOT_ID_REV,
                            display = {
                                "id": DISPLAY_HEADER,
                                "index": 0
                            }
                        ),
                        KemperActionDefinitions.AMP_ON_OFF()
                    ],
                    no = KemperActionDefinitions.EFFECT_ON_OFF(
                        slot_id = KemperMidi.EFFECT_SLOT_ID_DLY,
                        display = {
                            "id": DISPLAY_HEADER,
                            "index": 0
                        }
                    )
                )                
            ]
        },
        {
            "assignment": Switches.PA_MIDICAPTAIN_NANO_SWITCH_2,
            "actions": [
                KemperActionDefinitions.EFFECT_ON_OFF(
                    slot_id = KemperMidi.EFFECT_SLOT_ID_B,
                    display = {
                        "id": DISPLAY_HEADER,
                        "index": 1
                    },
                    mode = PushButtonModes.MOMENTARY
                )
            ]
        },
        {
            "assignment": Switches.PA_MIDICAPTAIN_NANO_SWITCH_A,
            "actions": [
                KemperActionDefinitions.AMP_ON_OFF(
                    display = {
                        "id": DISPLAY_FOOTER,
                        "index": 0
                    },
                    color = (Colors.WHITE, Colors.YELLOW, Colors.LIGHT_GREEN)  
                )
            ]
        },
        {
            "assignment": Switches.PA_MIDICAPTAIN_NANO_SWITCH_B,
            "actions": [
                KemperActionDefinitions.RESET_RIG_INFO_DISPLAYS(),
                KemperActionDefinitions.RIG_SELECT(
                    rig = 1,
                    bank = 1,

                    rig_off = 5,
                    bank_off = 3,

                    display = {
                        "id": DISPLAY_FOOTER,
                        "index": 1
                    }   
                )
            ]
        }
    ],

    # Optional: Override brightness settings for all switch LEDs. Range: [0..1]
    #"ledBrightness": {
    #    "on": FootSwitchDefaults.DEFAULT_BRIGHTNESS_ON,
    #    "off": FootSwitchDefaults.DEFAULT_BRIGHTNESS_OFF,
    #},

    # Optional: Factor used to dim the colors in the display (not the switches!) Range [0..1]
    #"displayDimFactorOn": DisplayDefaults.DEFAULT_SLOT_DIM_FACTOR_ON,
    #"displayDimFactorOff": DisplayDefaults.DEFAULT_SLOT_DIM_FACTOR_OFF,

## MIDI and other Options ################################################################################################################

    # Value provider which is responsible for setting values on MIDI messages for value changes, and parse MIDI messages
    # when an answer to a value request is received.
    "valueProvider": KemperMidiValueProvider(),

    # Max. milliseconds until a request is being terminated and it is
    # assumed that the Kemper device is offline. Optional, default is KemperDefinitions.DEFAULT_MAX_REQUEST_LIFETIME_MILLIS.
    #"maxRequestLifetimeMillis": ProcessingConfig.DEFAULT_MAX_REQUEST_LIFETIME_MILLIS,

    # Selects the MIDI channel to use [1..16]
    #"midiChannel": 1,

    # MIDI buffer size (60 is a good value)
    #"midiBufferSize": 60,

    # Update interval, for updating the rig date (which triggers all other data to update when changed) (milliseconds)
    # and other displays if assigned. 200 is a good value.
    #"updateInterval": 2000,

## Development Options ###################################################################################################################

    # Shows an area with statistics about frame processing time and available RAM (for debugging)
    "showFrameStats": True,

    # Optional, shows the effect slot names for EffectEnableAction
    #"showEffectSlotNames": True,

    # Debug mode, optional. Shows verbose console output. You can listen to that on the serial port via USB on your computer,
    # see https://learn.adafruit.com/welcome-to-circuitpython/advanced-serial-console-on-mac-and-linux 
    #"debug": True,

    #"debugUserInterfaceStructure": True,             # Show UI structure after init 
    #"debugDisplay": True,                            # Show verbose messages from the display elements. Optional.
    #"debugActions": True,                            # Show verbose messages from actions. Optional.
    #"actionsDebugSwitchName": "1",                   # Optional, can be set to a switch assignment name (see Ports in definition.py)
                                                      # to only show action messages for the switch mentioned
    #"debugSwitches": True,                           # Show verbose output for switches (color, brightness) or a switches 
                                                      # actions are triggered. Optional.
    #"debugParameters": True,                         # Show messages from the global parameter controller
    #"debugClient": True,                             # Show all requests and responses to/from the Kemper Profiler. Optional.
    #"clientDebugMapping": KemperMappings.NEXT_BANK,  # Optional, if set the kemper classes will only output messages related to
                                                      # the specified mapping.
    #"debugClientRawMidi": True,                      # Debug raw kemper MIDI messages. Only regarded whe "debugKemper" is enabled, too.
    #"debugMidi": True,                               # Debug Adafruit MIDI controller. Normally it is sufficient and more readable 
                                                      # to enable "debugKemperRawMidi" instead, which also shows the MIDI messages sent
                                                      # and received. Optional.
    #"debugConditions": True,                         # Debug condition evaluation

    # Set this to True to boot into explore mode. This mode listens to all GPIO pins available
    # and outputs the ID of the last pushed one, and also rotates through all available NeoPixels. 
    # Use this to detect the switch assignments on unknown devices. Optional.
    #"exploreMode": True
}

## User Interface ############################################################################################################################

# DisplayLabel default layout used for the action displays in header and footer
Config["actionLabelLayout"] = {
    "font": "/fonts/H20.pcf",
    "backColor": Colors.DEFAULT_LABEL_COLOR,
    #"cornerRadius": 5,
    "stroke": 1
}

#############################################################################################################################################

# Just used here locally!
DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 240
SLOT_HEIGHT = 40                 # Slot height on the display
DETAIL_HEIGHT = 20               # Height of the detail (amp/cab) display

# The Bounds class is used to easily layout the display. Initialize it with all available space:
bounds = DisplayBounds(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT)
 
# Defines the areas to be shown on the TFT display, and which values to show there.
Config["displays"] = [
    # Header area (referenced by ID in the action configurations)
    DisplaySplitContainer(
        id = DISPLAY_HEADER,
        name = "Header",
        bounds = bounds.remove_from_top(SLOT_HEIGHT)
    ),

    # Footer area (referenced by ID in the action configurations)
    DisplaySplitContainer(
        id = DISPLAY_FOOTER,
        name = "Footer",
        bounds = bounds.remove_from_bottom(SLOT_HEIGHT)
    ),

    # Rig name
    ParameterDisplayLabel(
        name = "Rig Name",
        bounds = bounds,   # Takes what is left over

        layout = ParameterCondition(
            mapping = KemperMappings.RIG_NAME,
            mode = ParameterConditionModes.MODE_STRING_NOT_CONTAINS,
            ref_value = "Q",

            yes = {
                "font": "/fonts/PTSans-NarrowBold-40.pcf",
                "lineSpacing": 0.8,
                "maxTextWidth": 220,
                "backColor": Colors.BLACK
            },

            no =  {
                "font": "/fonts/PTSans-NarrowBold-40.pcf",
                "lineSpacing": 0.8,
                "maxTextWidth": 220,
                "backColor": Colors.ORANGE
            }
        ),

        parameter = {
            "mapping": KemperMappings.RIG_NAME,
            "depends": KemperMappings.RIG_DATE,  # Only update this when the rig date changed (optional)
            "textOffline": "Kemper Profiler (offline)",
            "textReset": "Loading Rig..."
        }
    ),

    # Detail area (amp/cab etc.)
    ParameterDisplayLabel(
        name = "Rig Detail",
        bounds = bounds.bottom(DETAIL_HEIGHT),
        layout = {
            "font": "/fonts/A12.pcf"
        },
        parameter = {
            "mapping": KemperMappings.AMP_NAME,
            "depends": KemperMappings.RIG_DATE   # Only update this when the rig date changed (optional)
        }        
    ),

    # Statistics area (used internally, ID is fixed)
    DisplayLabel(
        id = DisplayAreas.STATISTICS,
        name = "Statistics",
        bounds = bounds.top(DETAIL_HEIGHT),
        layout = {
            "font": "/fonts/A12.pcf",
            "backColor": Colors.DEFAULT_LABEL_COLOR
        }        
    ),

    # Performance indicator (dot)
    PerformanceIndicator(
        id = DisplayAreas.PERFORMANCE_INDICATOR,
        name = "Dot",
        bounds = bounds.top(
                DisplayAreas.PERFORMANCE_INDICATOR_SIZE
            ).right(
                DisplayAreas.PERFORMANCE_INDICATOR_SIZE
            ).translated(
                - DisplayAreas.PERFORMANCE_INDICATOR_MARGIN, 
                DisplayAreas.PERFORMANCE_INDICATOR_MARGIN
            )
    )
]