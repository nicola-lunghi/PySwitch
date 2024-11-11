##############################################################################################################################################
# 
# Definition of display elememts.
#
##############################################################################################################################################

from micropython import const
from pyswitch.misc import Colors, PYSWITCH_VERSION
from pyswitch.controller.ConditionTree import ParameterCondition

from pyswitch.ui.elements import ParameterDisplayLabel, DisplaySplitContainer, DisplayBounds, DisplayLabel, TunerDisplay
from pyswitch.ui.ui import HierarchicalDisplayElement
from pyswitch.ui.StatisticalDisplays import BIDIRECTIONAL_PROTOCOL_STATE_DOT, PERFORMANCE_DOT

from kemper import KemperMappings

#############################################################################################################################################

# IDs to address the display labels in the switch configuration
DISPLAY_ID_HEADER = const(10)
DISPLAY_ID_FOOTER = const(20)  

#############################################################################################################################################

# Some only locally used constants
_DISPLAY_WIDTH = const(240)
_DISPLAY_HEIGHT = const(240)
_SLOT_HEIGHT = const(40)                 # Slot height on the display

#############################################################################################################################################

# The DisplayBounds class is used to easily layout the display in a subtractive way. Initialize it with all available space:
_bounds = DisplayBounds(0, 0, _DISPLAY_WIDTH, _DISPLAY_HEIGHT)
 
# Defines the areas to be shown on the TFT display, and which values to show there.
Display = ParameterCondition(
    mapping = KemperMappings.TUNER_MODE_STATE,
    ref_value = 1,
    mode = ParameterCondition.NOT_EQUAL,

    # Show normal display
    yes = HierarchicalDisplayElement(
        children = [
            # Header area (referenced by ID in the action configurations)
            DisplaySplitContainer(
                id = DISPLAY_ID_HEADER,
                bounds = _bounds.remove_from_top(_SLOT_HEIGHT)
            ),

            # Footer area (referenced by ID in the action configurations)
            DisplaySplitContainer(
                id = DISPLAY_ID_FOOTER,
                bounds = _bounds.remove_from_bottom(_SLOT_HEIGHT)
            ),

            # Rig name
            ParameterDisplayLabel(
                bounds = _bounds,   # Takes what is left over

                layout = {
                    "font": "/fonts/PTSans-NarrowBold-40.pcf",
                    "lineSpacing": 0.8,
                    "maxTextWidth": 220
                },

                parameter = {
                    "mapping": KemperMappings.RIG_NAME,
                    "textOffline": "Kemper Control " + PYSWITCH_VERSION,
                    "textReset": "Loading Rig..."
                }
            ),

            # Statistics area
            #STATS_DISPLAY(bounds),

            # Bidirectional protocol state indicator (dot)
            BIDIRECTIONAL_PROTOCOL_STATE_DOT(_bounds),

            # Performance indicator (dot)
            PERFORMANCE_DOT(_bounds.translated(0, 7)),
        ]
    ),

    # Show tuner display (only useful if bidirectional communication is enabled)
    no = TunerDisplay(
        mapping_note = KemperMappings.TUNER_NOTE,
        mapping_deviance = KemperMappings.TUNER_DEVIANCE,
        
        bounds = DisplayBounds(0, 0, _DISPLAY_WIDTH, _DISPLAY_HEIGHT),
        
        scale = 6,
        layout = {
            "font": "/fonts/PTSans-NarrowBold-40.pcf",
            "text": "Tuner"
        }
    )
)