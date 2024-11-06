##############################################################################################################################################
# 
# Definition of display elememts.
#
##############################################################################################################################################

from pyswitch.misc import Colors
from pyswitch.controller.ConditionTree import ParameterCondition, ParameterConditionModes

from pyswitch.ui.elements import ParameterDisplayLabel, DisplaySplitContainer, DisplayBounds, DisplayLabel, TunerDisplay
from pyswitch.ui.ui import HierarchicalDisplayElement
from pyswitch.ui.StatisticalDisplays import StatisticalDisplays

from kemper import KemperMappings

#############################################################################################################################################

# IDs to address the display labels in the switch configuration
class DisplayIds:
    DISPLAY_HEADER = 10
    DISPLAY_FOOTER = 20  
    DISPLAY_TUNER = 30
    DISPLAY_BOOST = 40

#############################################################################################################################################

# Some only locally used constants
DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 240
SLOT_HEIGHT = 40                 # Slot height on the display
DETAIL_HEIGHT = 20               # Height of the detail (amp/cab) display

#############################################################################################################################################

# The DisplayBounds class is used to easily layout the display in a subtractive way. Initialize it with all available space:
bounds = DisplayBounds(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT)
 
# Defines the areas to be shown on the TFT display, and which values to show there.
Display = ParameterCondition(
    mapping = KemperMappings.TUNER_MODE_STATE,
    ref_value = 1,
    mode = ParameterConditionModes.MODE_NOT_EQUAL,

    # Show normal display
    yes = HierarchicalDisplayElement(
        children = [
            # Header area (referenced by ID in the action configurations)
            DisplaySplitContainer(
                id = DisplayIds.DISPLAY_HEADER,
                name = "Header",
                bounds = bounds.remove_from_top(SLOT_HEIGHT)
            ),

            # Footer area (referenced by ID in the action configurations)
            DisplaySplitContainer(
                id = DisplayIds.DISPLAY_FOOTER,
                name = "Footer",
                bounds = bounds.remove_from_bottom(SLOT_HEIGHT)
            ),

            # Rig name
            ParameterDisplayLabel(
                name = "Rig Name",
                bounds = bounds,   # Takes what is left over

                layout = {
                    "font": "/fonts/PTSans-NarrowBold-40.pcf",
                    "lineSpacing": 0.8,
                    "maxTextWidth": 220
                },

                parameter = {
                    "mapping": KemperMappings.RIG_NAME,
                    "textOffline": "Kemper Profiler (offline)",
                    "textReset": "Loading Rig..."
                }
            ),

            DisplayLabel(
                id = DisplayIds.DISPLAY_TUNER,
                bounds = bounds.top(20).right(60),
                layout = {
                    "font": "/fonts/A12.pcf",
                    "backColor": Colors.BLACK   # Must be set because the action will set a back color later
                },
            ),

            DisplayLabel(
                id = DisplayIds.DISPLAY_BOOST,
                bounds = bounds.bottom(20).right(60),
                layout = {
                    "font": "/fonts/A12.pcf",
                    "backColor": Colors.BLACK   # Must be set because the action will set a back color later
                },
            ),

            # Statistics area
            #StatisticalDisplays.STATS_DISPLAY(bounds),

            # Bidirectional protocol state indicator (dot)
            StatisticalDisplays.BIDIRECTIONAL_PROTOCOL_STATE_DOT(bounds),

            # Performance indicator (dot)
            StatisticalDisplays.PERFORMANCE_DOT(bounds.translated(0, 7)),
        ]
    ),

        # Show tuner display (only useful if bidirectional communication is enabled)
        no = TunerDisplay(
            mapping_note = KemperMappings.TUNER_NOTE,
            mapping_deviance = KemperMappings.TUNER_DEVIANCE,
            
            bounds = DisplayBounds(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT),
            
            scale = 3,
            layout = {
                "font": "/fonts/PTSans-NarrowBold-40.pcf",
                "text": "Tuner"
            }
        )
    )