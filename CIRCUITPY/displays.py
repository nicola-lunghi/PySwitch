##############################################################################################################################################
# 
# Definition of display elememts.
#
##############################################################################################################################################
 
from pyswitch.core.misc import Colors
from pyswitch.core.controller.ConditionTree import ParameterCondition, ParameterConditionModes

from pyswitch.ui.elements.elements import ParameterDisplayLabel, DisplaySplitContainer, DisplayBounds
from pyswitch.ui.StatisticalDisplays import StatisticalDisplays

from kemper import KemperMappings

#############################################################################################################################################

# IDs to address the display labels in the switch configuration
class DisplayIds:
    DISPLAY_HEADER = 10
    DISPLAY_FOOTER = 20  

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
Displays = [        
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

    # Performance indicator (dot)
    StatisticalDisplays.PERFORMANCE_DOT(bounds),

    # Statistics area
    StatisticalDisplays.STATS_DISPLAY(bounds)
]
