##############################################################################################################################################
# 
# Definition of display elememts.
#
##############################################################################################################################################

from micropython import const
from pyswitch.misc import Callback, PYSWITCH_VERSION, DEFAULT_LABEL_COLOR #, Colors

from pyswitch.ui.elements import ParameterDisplayLabel, DisplaySplitContainer, DisplayBounds
from pyswitch.ui.elements import TunerDisplay, DisplayLabel, BIDIRECTIONAL_PROTOCOL_STATE_DOT, PERFORMANCE_DOT
from pyswitch.ui.ui import HierarchicalDisplayElement

from kemper import KemperMappings

#############################################################################################################################################

# Callback returning the splash(es) to show.
class _SplashCallback(Callback):
    def __init__(self):
        Callback.__init__(self)
        self.mapping = KemperMappings.TUNER_MODE_STATE()

    def get_mappings(self):
        yield self.mapping

    def get(self, data):
        if self.mapping.value != 1:
            return _SPLASH_DEFAULT
        else:
            return _SPLASH_TUNER

Splashes = _SplashCallback()

#############################################################################################################################################

# Layout used for the action labels (only used here locally)
_ACTION_LABEL_LAYOUT = {
    "font": "/fonts/H20.pcf",
    "backColor": DEFAULT_LABEL_COLOR,
    "stroke": 1
}

DISPLAY_HEADER_1 = DisplayLabel(layout = _ACTION_LABEL_LAYOUT, id = 1)
DISPLAY_HEADER_2 = DisplayLabel(layout = _ACTION_LABEL_LAYOUT, id = 2)
DISPLAY_FOOTER_1 = DisplayLabel(layout = _ACTION_LABEL_LAYOUT, id = 3)
DISPLAY_FOOTER_2 = DisplayLabel(layout = _ACTION_LABEL_LAYOUT, id = 4)

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

_SPLASH_DEFAULT = HierarchicalDisplayElement(
    bounds = _bounds_default,
    children = [
        # Header area (referenced by ID in the action configurations)
        DisplaySplitContainer(
            bounds = _bounds_default.remove_from_top(_SLOT_HEIGHT),
            children = [
                DISPLAY_HEADER_1,
                DISPLAY_HEADER_2
            ]
        ),

        # Footer area (referenced by ID in the action configurations)
        DisplaySplitContainer(
            bounds = _bounds_default.remove_from_bottom(_SLOT_HEIGHT),
            children = [
                DISPLAY_FOOTER_1,
                DISPLAY_FOOTER_2
            ]
        ),

        # Rig name
        ParameterDisplayLabel(
            bounds = _bounds_default,   # Takes what is left over

            layout = {
                "font": "/fonts/PTSans-NarrowBold-40.pcf",
                "lineSpacing": 0.8,
                "maxTextWidth": 220
            },

            parameter = {
                "mapping": KemperMappings.RIG_NAME(),
                "textOffline": "Kemper Control " + PYSWITCH_VERSION,
                "textReset": "Loading Rig..."
            },
            
            id = 10
        ),

        # Bidirectional protocol state indicator (dot)
        BIDIRECTIONAL_PROTOCOL_STATE_DOT(_bounds_default),

        # Performance indicator (dot)
        PERFORMANCE_DOT(_bounds_default.translated(0, 7)),
    ]
)

# Tuner display
_SPLASH_TUNER = TunerDisplay(
    mapping_note = KemperMappings.TUNER_NOTE(),
    mapping_deviance = KemperMappings.TUNER_DEVIANCE(),
    
    bounds = _display_bounds,
    
    scale = 3,
    layout = {
        "font": "/fonts/PTSans-NarrowBold-40.pcf"
    }
)
