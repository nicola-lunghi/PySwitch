##############################################################################################################################################
# 
# Definition of display elememts.
#
##############################################################################################################################################

from micropython import const
from pyswitch.misc import DEFAULT_LABEL_COLOR #, Colors

from pyswitch.ui.elements import DisplaySplitContainer, DisplayBounds
from pyswitch.ui.elements import DisplayLabel, BIDIRECTIONAL_PROTOCOL_STATE_DOT, PERFORMANCE_DOT
from pyswitch.ui.ui import HierarchicalDisplayElement

from pyswitch.clients.kemper import KemperRigNameCallback, TunerDisplayCallback

#############################################################################################################################################

# Layout used for the action labels (only used here locally)
_ACTION_LABEL_LAYOUT = {
    "font": "/fonts/H20.pcf",
    "backColor": DEFAULT_LABEL_COLOR,
    "stroke": 1
}

# Layout used for the action labels (only used here locally)
_ACTION_LABEL_LAYOUT_SMALL = {
    "font": "/fonts/A12.pcf",
    "backColor": DEFAULT_LABEL_COLOR,
    "stroke": 1
}

#############################################################################################################################################

# Some only locally used constants
_DISPLAY_WIDTH = const(240)
_DISPLAY_HEIGHT = const(240)
_SLOT_HEIGHT = const(40)                 # Slot height on the display

#############################################################################################################################################

# The DisplayBounds class is used to easily layout the default display in a subtractive way. Initialize it with all available space:
_display_bounds = DisplayBounds(0, 0, _DISPLAY_WIDTH, _DISPLAY_HEIGHT)

# Default display
_bounds_default = _display_bounds.clone()

_contents_default = []

# Header area (referenced by ID in the action configurations)
DISPLAY_HEADER_1 = DisplayLabel(layout = _ACTION_LABEL_LAYOUT)
DISPLAY_HEADER_2 = DisplayLabel(layout = _ACTION_LABEL_LAYOUT)

_contents_default.append(
    DisplaySplitContainer(
        bounds = _bounds_default.remove_from_top(_SLOT_HEIGHT),
        children = [
            DISPLAY_HEADER_1,
            DISPLAY_HEADER_2
        ]
    )
)

# Footer area (referenced by ID in the action configurations)
DISPLAY_FOOTER_1 = DisplayLabel(layout = _ACTION_LABEL_LAYOUT)
DISPLAY_FOOTER_2 = DisplayLabel(layout = _ACTION_LABEL_LAYOUT)

_contents_default.append(
    DisplaySplitContainer(
        bounds = _bounds_default.remove_from_bottom(_SLOT_HEIGHT),
        children = [
            DISPLAY_FOOTER_1,
            DISPLAY_FOOTER_2
        ]
    )
)

# Extra display labels for switches 3 and C
_bounds_switch_c = _bounds_default.top(20).right(60)

DISPLAY_SWITCH_3 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT_SMALL,
    bounds = _bounds_switch_c
)

_contents_default.append(DISPLAY_SWITCH_3)

DISPLAY_SWITCH_C = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT_SMALL,
    bounds = _bounds_default.bottom(20).right(60)
)

_contents_default.append(DISPLAY_SWITCH_C)
    
# Rig name
_contents_default.append(
    DisplayLabel(
        bounds = _bounds_default,   # Takes what is left over

        layout = {
            "font": "/fonts/PTSans-NarrowBold-40.pcf",
            "lineSpacing": 0.8,
            "maxTextWidth": 220,
            "text": KemperRigNameCallback.DEFAULT_TEXT,
        },

        callback = KemperRigNameCallback()
    )
)

# Bidirectional protocol state indicator (dot)
_contents_default.append(BIDIRECTIONAL_PROTOCOL_STATE_DOT(_bounds_switch_c.translated(0, 20)))

# Performance indicator (dot)
_contents_default.append(PERFORMANCE_DOT(_bounds_switch_c.translated(0, 27)))


Splashes = TunerDisplayCallback(
    splash_default = HierarchicalDisplayElement(
        bounds = _bounds_default,
        children = _contents_default
    )
)
