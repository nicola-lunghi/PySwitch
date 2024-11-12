##############################################################################################################################################
# 
# Definition of actions for switches
#
##############################################################################################################################################
 
from pyswitch.hardware.Hardware import Hardware

from pyswitch.misc import Colors, Defaults
#from pyswitch.controller.ConditionTree import ParameterCondition
from pyswitch.controller.actions.actions import PushButtonAction, ParameterAction, HoldAction

from kemper import KemperActionDefinitions, KemperEffectSlot, KemperMappings
from display import DISPLAY_ID_FOOTER, DISPLAY_ID_HEADER


# Layout used for the action labels (only used here locally)
_ACTION_LABEL_LAYOUT = {
    "font": "/fonts/H20.pcf",
    "backColor": Defaults.DEFAULT_LABEL_COLOR,
    "stroke": 1
}

# Defines the switch assignments
Switches = [

    # Switch 1
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_1,
        "actions": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A,
                display = {
                    "id": DISPLAY_ID_HEADER,
                    "index": 0,
                    "layout": _ACTION_LABEL_LAYOUT
                }
            )                         
        ]
    },

    # Switch 2
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_2,
        "actions": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_B,
                display = {
                    "id": DISPLAY_ID_HEADER,
                    "index": 1,
                    "layout": _ACTION_LABEL_LAYOUT
                }
            )
        ]
    },

    # Switch A
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_A,
        "actions": [
            ParameterAction({
                "mapping": KemperMappings.FREEZE(KemperEffectSlot.EFFECT_SLOT_ID_REV),
                "display": {
                    "id": DISPLAY_ID_FOOTER,
                    "index": 0,
                    "layout": _ACTION_LABEL_LAYOUT
                },
                "text": "RvFreeze",
                "color": Colors.DARK_GREEN,
                "mode": PushButtonAction.MOMENTARY
            })
        ]
    },
    
    # Switch B
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_B,
        "actions": [
            KemperActionDefinitions.TAP_TEMPO(
                display = {
                    "id": DISPLAY_ID_FOOTER,
                    "index": 1,
                    "layout": _ACTION_LABEL_LAYOUT
                },
                color = Colors.LIGHT_GREEN
            )
        ]
    }
]
