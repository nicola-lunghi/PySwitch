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
from pyswitch.controller.callbacks import Callback

from pyswitch.clients.kemper import KemperRigNameCallback, TunerDisplayCallback, KemperMappings

#############################################################################################################################################

# Layout used for the action labels (only used here locally)
_ACTION_LABEL_LAYOUT = {
    "font": "/fonts/H20.pcf",
    "backColor": DEFAULT_LABEL_COLOR,
    "stroke": 1
}

DISPLAY_HEADER_1 = DisplayLabel(layout = _ACTION_LABEL_LAYOUT)
DISPLAY_HEADER_2 = DisplayLabel(layout = _ACTION_LABEL_LAYOUT)
DISPLAY_FOOTER_1 = DisplayLabel(layout = _ACTION_LABEL_LAYOUT)
DISPLAY_FOOTER_2 = DisplayLabel(layout = _ACTION_LABEL_LAYOUT)

#############################################################################################################################################

# Some only locally used constants
_DISPLAY_WIDTH = const(240)
_DISPLAY_HEIGHT = const(240)
_SLOT_HEIGHT = const(40)                 # Slot height on the display

#############################################################################################################################################

# Custom callback for amp name
class _AmpNameCallback(Callback):
    def __init__(self):
        Callback.__init__(self)
        
        # This defines that the following mappings have to be listened to
        self._mapping = KemperMappings.AMP_NAME()
        self.register_mapping(self._mapping)        

    # This will be called for updating the label whenever the mappings defined above
    # have changed.
    def update_label(self, label):
        amp_name = self._mapping.value

        if amp_name:
            label.text = amp_name
        else:
            label.text = ""

#############################################################################################################################################

# The DisplayBounds class is used to easily layout the default display in a subtractive way. Initialize it with all available space:
_display_bounds = DisplayBounds(0, 0, _DISPLAY_WIDTH, _DISPLAY_HEIGHT)

_bounds = _display_bounds.clone()

Splashes = TunerDisplayCallback(
    splash_default = HierarchicalDisplayElement(
        bounds = _display_bounds,
        children = [
            # Header area (referenced by ID in the action configurations)
            DisplaySplitContainer(
                bounds = _bounds.remove_from_top(_SLOT_HEIGHT),
                children = [
                    DISPLAY_HEADER_1,
                    DISPLAY_HEADER_2
                ]
            ),

            # Footer area (referenced by ID in the action configurations)
            DisplaySplitContainer(
                bounds = _bounds.remove_from_bottom(_SLOT_HEIGHT),
                children = [
                    DISPLAY_FOOTER_1,
                    DISPLAY_FOOTER_2
                ]
            ),

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
