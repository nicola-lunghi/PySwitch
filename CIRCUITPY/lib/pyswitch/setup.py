##############################################################################################################################################
# 
# Device mapping and displays
#
##############################################################################################################################################
 
from .definitions import Colors, StatisticMeasurementTypes
from .switches import Switches

from .core.controller.conditions.ParameterCondition import ParameterCondition, ParameterConditionModes
from .core.controller.actions.base.PushButtonAction import PushButtonModes
from .core.controller.measurements import RuntimeMeasurement

from pyswitch_kemper.Kemper import Kemper
from pyswitch_kemper.KemperMappings import KemperMappings
from pyswitch_kemper.KemperActionDefinitions import KemperActionDefinitions
from lib.pyswitch_kemper.KemperEffectSlot import KemperEffectSlot
from pyswitch_kemper.KemperMidiValueProvider import KemperMidiValueProvider

from .ui.DisplayBounds import DisplayBounds
from .ui.elements.DisplayLabel import DisplayLabelLayout
from .ui.elements.ParameterDisplayLabel import ParameterDisplayLabel
#from .ui.elements.StatisticsDisplayLabel import StatisticsDisplayLabel
from .ui.elements.DisplaySplitContainer import DisplaySplitContainer
from .ui.elements.PerformanceIndicator import PerformanceIndicator

# Custom (local) display IDs. Just used locally here to reference header and footer display areas in the action definitions.
DISPLAY_HEADER = 10
DISPLAY_FOOTER = 20  

Setup = {

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
                    ref_value = Kemper.NRPN_VALUE(0.5),

                    yes = [
                        KemperActionDefinitions.EFFECT_ON_OFF(
                            id = "sw1",
                            slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A,
                        ),
                        KemperActionDefinitions.EFFECT_ON_OFF(
                            slot_id = KemperEffectSlot.EFFECT_SLOT_ID_REV,
                            display = {
                                "id": DISPLAY_HEADER,
                                "index": 0
                            }
                        ),
                        KemperActionDefinitions.AMP_ON_OFF()
                    ],
                    no = KemperActionDefinitions.EFFECT_ON_OFF(
                        slot_id = KemperEffectSlot.EFFECT_SLOT_ID_DLY,
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
                    slot_id = KemperEffectSlot.EFFECT_SLOT_ID_B,
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
        },

        ##################################################

        #{
        #    "assignment": { "model": AdafruitSwitch(board.GP2) },
        #    "actions": [
        #        KemperActionDefinitions.EFFECT_ON_OFF(
        #            slot_id = KemperEffectSlots.EFFECT_SLOT_ID_B,
        #            display = {
        #                "id": DISPLAY_FOOTER2,
        #                "index": 0
        #            }
        #        )          
        #    ]
        #},

        #{
        #    "assignment": { "model": AdafruitSwitch(board.GP3) },
        #    "actions": [
        #        KemperActionDefinitions.AMP_ON_OFF(
        #            display = {
        #                "id": DISPLAY_FOOTER2,
         #               "index": 1
         #           }   
        #        )                
        #    ]
        #},


        #{ "assignment": { "model": AdafruitSwitch(board.GP4) }, "actions": [ KemperActionDefinitions.TUNER_MODE() ] },
        #{ "assignment": { "model": AdafruitSwitch(board.GP22) }, "actions": [ KemperActionDefinitions.TUNER_MODE() ] },
        #{ "assignment": { "model": AdafruitSwitch(board.GP23) }, "actions": [ KemperActionDefinitions.TUNER_MODE() ] },
        #{ "assignment": { "model": AdafruitSwitch(board.GP24) }, "actions": [ KemperActionDefinitions.TUNER_MODE() ] },

    ],

    # Value provider which is responsible for setting values on MIDI messages for value changes, and parse MIDI messages
    # when an answer to a value request is received.
    "valueProvider": KemperMidiValueProvider(),

    # Selects the MIDI channel to use [1..16] default is 1
    #"midiChannel": 1,
}

## User Interface ############################################################################################################################

# DisplayLabel default layout used for the action displays in header and footer
Setup["actionLabelLayout"] = DisplayLabelLayout({
    "font": "/fonts/H20.pcf",
    "backColor": Colors.DEFAULT_LABEL_COLOR,
    "stroke": 1
})

#############################################################################################################################################

# Just used here locally!
DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 240
SLOT_HEIGHT = 40                 # Slot height on the display
DETAIL_HEIGHT = 20               # Height of the detail (amp/cab) display

STAT_LINES = 3                   # Statistics number of lines
 
# Properties for the performance indicator (dot)
PERFORMANCE_INDICATOR_SIZE = 5
PERFORMANCE_INDICATOR_MARGIN = 2

# The Bounds class is used to easily layout the display. Initialize it with all available space:
bounds = DisplayBounds(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT)
 
# Defines the areas to be shown on the TFT display, and which values to show there.
Setup["displays"] = [
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

    # Footer area (referenced by ID in the action configurations)
    #DisplaySplitContainer(
    #    id = DISPLAY_FOOTER2,
    #    name = "Footer2",
    #    bounds = bounds.remove_from_bottom(SLOT_HEIGHT)
    #),

    # Rig name
    ParameterDisplayLabel(
        name = "Rig Name",
        bounds = bounds,   # Takes what is left over

        layout = ParameterCondition(
            mapping = KemperMappings.RIG_NAME,
            mode = ParameterConditionModes.MODE_STRING_NOT_CONTAINS,
            ref_value = "Q",

            yes = DisplayLabelLayout({
                "font": "/fonts/PTSans-NarrowBold-40.pcf",
                "lineSpacing": 0.8,
                "maxTextWidth": 220,
                "backColor": Colors.BLACK
            }),

            no =  DisplayLabelLayout({
                "font": "/fonts/PTSans-NarrowBold-40.pcf",
                "lineSpacing": 0.8,
                "maxTextWidth": 220,
                "backColor": Colors.ORANGE
            })
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
        layout = DisplayLabelLayout({
            "font": "/fonts/A12.pcf"
        }),
        parameter = {
            "mapping": KemperMappings.AMP_NAME,
            "depends": KemperMappings.RIG_DATE   # Only update this when the rig date changed (optional)
        }        
    ),

    # Performance indicator (dot)
    PerformanceIndicator(        
        measurement = RuntimeMeasurement(StatisticMeasurementTypes.TICK_TIME, interval_millis = 200),
        name = "Dot",
        bounds = bounds.top(
                PERFORMANCE_INDICATOR_SIZE
            ).right(
                PERFORMANCE_INDICATOR_SIZE
            ).translated(
                - PERFORMANCE_INDICATOR_MARGIN, 
                PERFORMANCE_INDICATOR_MARGIN
            )
    ),

    # Statistics area (used internally, ID is fixed)
    #StatisticsDisplayLabel(
    #    bounds = bounds.top(DETAIL_HEIGHT * STAT_LINES),
    #    layout = DisplayLabelLayout({
    #        "font": "/fonts/A12.pcf"
    #    }),
    #    measurements = [
    #        RuntimeMeasurement(StatisticMeasurementTypes.TICK_TIME, interval_millis = 1000),
    #        #RuntimeMeasurement(StatisticMeasurementTypes.SWITCH_UPDATE_TIME, interval_millis = 1000),   # This measurement costs a lot of overhead!
    #        FreeMemoryMeasurement()
    #    ]
    #)
]