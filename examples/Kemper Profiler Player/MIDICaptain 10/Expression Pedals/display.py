##############################################################################################################################################
# 
# Definition of display elememts.
#
##############################################################################################################################################

from micropython import const
from pyswitch.misc import DEFAULT_LABEL_COLOR #, Colors

from pyswitch.ui.ui import DisplayElement, DisplayBounds
from pyswitch.ui.elements import DisplayLabel, BidirectionalProtocolState

from pyswitch.clients.kemper import KemperRigNameCallback, TunerDisplayCallback

#############################################################################################################################################

# Layout used for the action labels (only used here locally)
_ACTION_LABEL_LAYOUT = {
    "font": "/fonts/H20.pcf",
    "backColor": DEFAULT_LABEL_COLOR,
    "stroke": 1
}

#############################################################################################################################################

# Some only locally used constants
_DISPLAY_WIDTH = const(240)
_DISPLAY_HEIGHT = const(240)
_SLOT_WIDTH = const(120)                 # Slot width on the display
_SLOT_HEIGHT = const(40)                 # Slot height on the display
_FOOTER_Y = const(200)
_RIG_NAME_HEIGHT = const(160)

#############################################################################################################################################

# Header
DISPLAY_HEADER_1 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT,
    bounds = DisplayBounds(0, 0, 80, _SLOT_HEIGHT)
)
DISPLAY_HEADER_2 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT,
    bounds = DisplayBounds(80, 0, 80, _SLOT_HEIGHT)
)
DISPLAY_HEADER_3 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT,
    bounds = DisplayBounds(160, 0, 80, _SLOT_HEIGHT)
)

# Footer
DISPLAY_FOOTER_1 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT,
    bounds = DisplayBounds(0, _FOOTER_Y, _SLOT_WIDTH, _SLOT_HEIGHT)
)
DISPLAY_FOOTER_2 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT,
    bounds = DisplayBounds(_SLOT_WIDTH, _FOOTER_Y, _SLOT_WIDTH, _SLOT_HEIGHT)
)

# Page
DISPLAY_PAGE = DisplayLabel(
    layout = {
        "font": "/fonts/A12.pcf",
        "backColor": (0, 0, 0)
    },
    bounds = DisplayBounds(0, _FOOTER_Y - 20, _DISPLAY_WIDTH, 20)
)

Splashes = TunerDisplayCallback(
    strobe = True,
    splash_default = DisplayElement(
        bounds = DisplayBounds(0, 0, _DISPLAY_WIDTH, _DISPLAY_HEIGHT),
        children = [
            # Header area 
            DISPLAY_HEADER_1,
            DISPLAY_HEADER_2,
            DISPLAY_HEADER_3,

            # Footer area 
            DISPLAY_FOOTER_1,
            DISPLAY_FOOTER_2,

            # Rig name
            DisplayLabel(
                bounds = DisplayBounds(
                    0, 
                    _SLOT_HEIGHT,
                    _DISPLAY_WIDTH,
                    _RIG_NAME_HEIGHT
                ),

                layout = {
                    "font": "/fonts/PTSans-NarrowBold-40.pcf",
                    "lineSpacing": 0.8,
                    "maxTextWidth": 220,
                    "text": KemperRigNameCallback.DEFAULT_TEXT,
                },

                callback = KemperRigNameCallback()
            ),

            # Pager
            DISPLAY_PAGE,

            # Bidirectional protocol state indicator (dot)
            BidirectionalProtocolState(DisplayBounds(
                0, 
                _SLOT_HEIGHT,
                _DISPLAY_WIDTH,
                _RIG_NAME_HEIGHT
            ))
        ]
    )
)
