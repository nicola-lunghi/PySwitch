#################################################################################################################################
# 
# Defines the display layout. The areas defined here can be used in the config later.
#
#################################################################################################################################

from .definitions import Colors
from .src.ui.DisplayBounds import DisplayBounds

from .src.ui.elements.DisplayLabel import DisplayLabel
from .src.ui.elements.DisplaySplitContainer import DisplaySplitContainer
from .src.ui.elements.PerformanceIndicator import PerformanceIndicator

#################################################################################################################################

# Just used locally here!
DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 240
SLOT_HEIGHT = 40                 # Slot height on the display
DETAIL_HEIGHT = 20               # Height of the detail (amp/cab) display

PERFORMANCE_INDICATOR_SIZE = 5
PERFORMANCE_INDICATOR_MARGIN = 2

#################################################################################################################################


# Display area IDs. These are only used in the config to address the display areas. IDs should not be zero (technically no 
# problem, but the program will not find the correct elements because zero is the default ID for all elements)
class DisplayAreas:
    # Areas for user information. Can be freely changed (not used inside the program itself, just in config)
    HEADER = 10
    FOOTER = 20   
    RIG_NAME = 30
    DETAIL = 40

    # Statistics area (only shown if enabled in config). Must exist (called by the program directly),
    # however the actual value does not matter.
    STATISTICS = 999

    # Shows a small dot indicating loop processing time (not visible when max. tick time is way below the updateInterval, warning
    # the user when tick time gets higher and shows an alert when tick time is higher than the update interval, which means that
    # the device is running on full capacity. If tick time is more than double the update interval, an even more severe alert is shown)
    PERFORMANCE_INDICATOR = 1000

    # DisplayLabel layout used for the action displays
    ACTION_LABEL_LAYOUT = {
        "font": "/fonts/H20.pcf",
        "backColor": Colors.DEFAULT_LABEL_COLOR,
        "cornerRadius": 5,
        "stroke": 1
    }


#################################################################################################################################

# The Bounds class is used to easily layout the display. Initialize it with all available space:
bounds = DisplayBounds(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT)
 
# Display area definitions. Must be a list of DisplayElement instances.
DisplayAreaDefinitions = [
    # Header area
    DisplaySplitContainer(
        id = DisplayAreas.HEADER,
        name = "Header",
        bounds = bounds.remove_from_top(SLOT_HEIGHT)
    ),

    # Footer area
    DisplaySplitContainer(
        id = DisplayAreas.FOOTER,
        name = "Footer",
        bounds = bounds.remove_from_bottom(SLOT_HEIGHT)
    ),

    # Detail area (amp/cab etc.)
    DisplayLabel(
        id = DisplayAreas.DETAIL,
        name = "Detail",
        bounds = bounds.bottom(DETAIL_HEIGHT),
        layout = {
            "font": "/fonts/A12.pcf"
        }
    ),

    # Statistics area
    DisplayLabel(
        id = DisplayAreas.STATISTICS,
        name = "Statistics",
        bounds = bounds.top(DETAIL_HEIGHT),
        layout = {
            "font": "/fonts/A12.pcf",
            "backColor": Colors.DEFAULT_LABEL_COLOR   # TODO is this really working?
        }        
    ),

    # Performance indicator (dot)
    PerformanceIndicator(
        id = DisplayAreas.PERFORMANCE_INDICATOR,
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

    # Rig name
    DisplayLabel(
        id = DisplayAreas.RIG_NAME,
        name = "Info",
        bounds = bounds,   # Takes what is left over
        layout = {
            "font": "/fonts/PTSans-NarrowBold-40.pcf",
            "lineSpacing": 0.8,
            "maxTextWidth": 220
        }
    )
]

