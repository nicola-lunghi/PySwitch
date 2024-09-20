#################################################################################################################################
# 
# Defines the display layout. The areas defined here can be used in the config later.
#
#################################################################################################################################

from .definitions import KemperDefinitions, Colors

#################################################################################################################################

# Just used locally here!
DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 240
SLOT_HEIGHT = 40           # Slot height on the display

#################################################################################################################################


# Display area IDs for the (optional) switch displays
class DisplayAreas:
    HEADER = 0
    FOOTER = 10
    INFO = 100
    STATISTICS = 200


#################################################################################################################################
 
 
# Display area definitions. The areas are created in the order they are defined here.
DisplayAreaDefinitions = [
    # Info area (rig name etc.)
    {
        "id": DisplayAreas.INFO,
        "name": "Info",

        "x": 0,
        "y": 0,
        "width": DISPLAY_WIDTH,
        "height": DISPLAY_HEIGHT,
        
        # Layout for the info area (rig name) label
        "layout": {
            "font": "/fonts/PTSans-NarrowBold-40.pcf",
            "lineSpacing": 0.8,
            "maxTextWidth": 220,
            "text": KemperDefinitions.OFFLINE_RIG_NAME     # Initial text
        },
    },

    # Header area
    {
        "id": DisplayAreas.HEADER,
        "name": "Header",

        "x": 0,
        "y": 0,
        "width": DISPLAY_WIDTH,
        "height": SLOT_HEIGHT,
        
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

        "x": 0,
        "y": DISPLAY_HEIGHT - SLOT_HEIGHT,
        "width": DISPLAY_WIDTH,
        "height": SLOT_HEIGHT,

        "layout": {
            "font": "/fonts/H20.pcf",
            "backColor": Colors.DEFAULT_LABEL_COLOR,
            "cornerRadius": 5
        }        
    },

    # Statistics area
    {
        "id": DisplayAreas.STATISTICS,
        "name": "Statistics",

        "x": 0,
        "y": DISPLAY_HEIGHT - 2 * SLOT_HEIGHT,
        "width": DISPLAY_WIDTH,
        "height": SLOT_HEIGHT,

        "layout": {
            "font": "/fonts/H20.pcf",
            "backColor": Colors.DEFAULT_LABEL_COLOR
        }        
    }
]

