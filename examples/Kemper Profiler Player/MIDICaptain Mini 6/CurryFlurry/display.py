##############################################################################################################################################
# 
# Definition of display elememts.
#
##############################################################################################################################################

from micropython import const
from pyswitch.ui.elements import DisplaySplitContainer, DisplayBounds
from pyswitch.ui.elements import DisplayLabel, BIDIRECTIONAL_PROTOCOL_STATE_DOT, PERFORMANCE_DOT
from pyswitch.ui.ui import HierarchicalDisplayElement

from pyswitch.clients.kemper import KemperRigNameCallback, TunerDisplayCallback, KemperMappings

#############################################################################################################################################

# Some only locally used constants
_DISPLAY_WIDTH = const(240)
_DISPLAY_HEIGHT = const(240)

#############################################################################################################################################

# The DisplayBounds class is used to easily layout the default display in a subtractive way. Initialize it with all available space:
_display_bounds = DisplayBounds(0, 0, _DISPLAY_WIDTH, _DISPLAY_HEIGHT)

_bounds = _display_bounds.clone()

Splashes = TunerDisplayCallback(
    splash_default = HierarchicalDisplayElement(
        bounds = _display_bounds,
        children = [
            # Rig name
            DisplayLabel(
                bounds = _bounds,   # Takes what is left over

                layout = {
                    "font": "/fonts/PTSans-NarrowBold-40.pcf",
                    "lineSpacing": 0.8,
                    "maxTextWidth": 220,
                    "text": KemperRigNameCallback.DEFAULT_TEXT,
                },

                callback = KemperRigNameCallback()
            ),

            # Bidirectional protocol state indicator (dot)
            BIDIRECTIONAL_PROTOCOL_STATE_DOT(_bounds),

            # Performance indicator (dot)
            PERFORMANCE_DOT(_bounds.translated(0, 7)),
        ]
    )
)
