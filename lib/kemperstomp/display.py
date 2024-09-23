#################################################################################################################################
# 
# Defines the display layout. The areas defined here can be used in the config later.
#
#################################################################################################################################

from .definitions import KemperDefinitions, Colors
from .src.ui.Rectangle import Rectangle

#################################################################################################################################

# Just used locally here!
DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 240
SLOT_HEIGHT = 40           # Slot height on the display
DETAIL_HEIGHT = 20         # Height of the detail (amp/cab) display

#################################################################################################################################


# Display area IDs. These are only used in the config to address the display areas.
class DisplayAreas:
    # Areas for user information. Can be freely changed (not used inside the program itself, just in config)
    HEADER = 0
    FOOTER = 1    
    RIG_NAME = 2
    DETAIL = 3

    # Statistics area (only shown if enabled in config). Must exist (called by the program directly),
    # however the actual value does not matter.
    STATISTICS = 999


#################################################################################################################################

# Layouter instance, initialized to the available screen size.
bounds = Rectangle(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT)
 
# Display area definitions. See DisplayArea class.
# {
#      "id":     ID for the area to address it in the config
#      "name":   Readable name for the area (used in debugging only but must be defined)
#      "bounds": Bounds object (defines x/y/w/h)
#      "layout": A layout definition used for all labels inside the area. Also see DisplayLabel class.
#                {
#                    "font": Path to the font, example: "/fonts/H20.pcf". Mandatory.
#                    "maxTextWidth": Maximum text width in pixels, optional
#                    "lineSpacing": Line spacing (optional), float
#                    "textColor": Text color (default is None, which auto-detects a matching color)
#                    "backColor": Background color (default is None for no background at all)
#                    "cornerRadius": Corner radius (optional: default is 0)
#                    "text": Initial text (default is "")
#                }
# }
# 
# The Bounds class is used to easily layout the display, however, if you need overlapping areas, this is also allowed.
DisplayAreaDefinitions = [
    # Header area
    {
        "id": DisplayAreas.HEADER,
        "name": "Header",
        "bounds": bounds.remove_from_top(SLOT_HEIGHT),       
        "layout": {
            "font": "/fonts/H20.pcf",
            "backColor": Colors.DEFAULT_LABEL_COLOR,
            "cornerRadius": 5
        }
    },

    # Footer area
    {
        "id": DisplayAreas.FOOTER,
        "name": "Footer",
        "bounds": bounds.remove_from_bottom(SLOT_HEIGHT),
        "layout": {
            "font": "/fonts/H20.pcf",
            "backColor": Colors.DEFAULT_LABEL_COLOR,
            "cornerRadius": 5
        }        
    },

    # Detail area (amp/cab etc.)
    {
        "id": DisplayAreas.DETAIL,
        "name": "Detail",
        "bounds": bounds.bottom(DETAIL_HEIGHT),
        "layout": {
            "font": "/fonts/A12.pcf",
            "text": "Foo bar"
        }
    },

    # Statistics area
    {
        "id": DisplayAreas.STATISTICS,
        "name": "Statistics",
        "bounds": bounds.top(DETAIL_HEIGHT),
        "layout": {
            "font": "/fonts/A12.pcf",
            "backColor": Colors.DEFAULT_LABEL_COLOR
        }        
    },

    # Rig name
    {
        "id": DisplayAreas.RIG_NAME,
        "name": "Info",
        "bounds": bounds,   # Takes what is left over
        "layout": {
            "font": "/fonts/PTSans-NarrowBold-40.pcf",
            "lineSpacing": 0.8,
            "maxTextWidth": 220,
            "text": KemperDefinitions.OFFLINE_RIG_NAME     # Initial text
        }
    }
]

