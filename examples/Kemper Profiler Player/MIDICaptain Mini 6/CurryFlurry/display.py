##############################################################################################################################################
# 
# Definition of display elememts.
#
##############################################################################################################################################

from micropython import const

from pyswitch.ui.ui import DisplayElement, DisplayBounds
from pyswitch.ui.elements import DisplayLabel, BidirectionalProtocolState

from pyswitch.clients.kemper import KemperRigNameCallback, TunerDisplayCallback

#############################################################################################################################################

# Some only locally used constants
_DISPLAY_WIDTH = const(240)
_DISPLAY_HEIGHT = const(240)

#############################################################################################################################################

Splashes = TunerDisplayCallback(
    strobe = True,
    splash_default = DisplayElement(
        bounds = DisplayBounds(0, 0, _DISPLAY_WIDTH, _DISPLAY_HEIGHT),
        children = [
            # Rig name
            DisplayLabel(
                bounds = DisplayBounds(0, 0, _DISPLAY_WIDTH, _DISPLAY_HEIGHT),

                layout = {
                    "font": "/fonts/PTSans-NarrowBold-40.pcf",
                    "lineSpacing": 0.8,
                    "maxTextWidth": 220,
                    "text": KemperRigNameCallback.DEFAULT_TEXT,
                },

                callback = KemperRigNameCallback()
            ),

            # Bidirectional protocol state indicator (dot)
            BidirectionalProtocolState(DisplayBounds(0, 0, _DISPLAY_WIDTH, _DISPLAY_HEIGHT))
        ]
    )
)
