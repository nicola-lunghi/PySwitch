##############################################################################################################################################
# 
# Definition of actions for switches
#
##############################################################################################################################################
 
from pyswitch.hardware.hardware import SwitchDefinitions

from pyswitch.misc import Colors, Defaults
from pyswitch.controller.ConditionTree import ParameterCondition, ParameterConditionModes
from pyswitch.controller.actions.actions import PushButtonModes, ParameterAction, HoldAction

from kemper import KemperActionDefinitions, KemperEffectSlot, KemperMappings
from display import DisplayIds


# Layout used for the action labels (only used here locally)
ACTION_LABEL_LAYOUT = {
    "font": "/fonts/H20.pcf",
    "backColor": Defaults.DEFAULT_LABEL_COLOR,
    "stroke": 1
}

# Defines the switch assignments
Switches = [

    # Switch 1
    {
        "assignment": SwitchDefinitions.PA_MIDICAPTAIN_NANO_SWITCH_1,
        "actions": [
            KemperActionDefinitions.BANK_DOWN(
                display = {
                    "id": DisplayIds.DISPLAY_HEADER,
                    "index": 0,
                    "layout": ACTION_LABEL_LAYOUT
                }
            )                         
        ]
    },

    # Switch 2
    {
        "assignment": SwitchDefinitions.PA_MIDICAPTAIN_NANO_SWITCH_2,
        "actions": [
            KemperActionDefinitions.BANK_UP(
                display = {
                    "id": DisplayIds.DISPLAY_HEADER,
                    "index": 1,
                    "layout": ACTION_LABEL_LAYOUT
                }
            )
        ]
    },

    # Switch A
    {
        "assignment": SwitchDefinitions.PA_MIDICAPTAIN_NANO_SWITCH_A,
        "actions": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_DLY,
                display = {
                    "id": DisplayIds.DISPLAY_FOOTER,
                    "index": 0,
                    "layout": ACTION_LABEL_LAYOUT
                }
            )
        ]
    },
    
    # Switch B
    {
        "assignment": SwitchDefinitions.PA_MIDICAPTAIN_NANO_SWITCH_B,
        "actions": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_REV,
                display = {
                    "id": DisplayIds.DISPLAY_FOOTER,
                    "index": 1,
                    "layout": ACTION_LABEL_LAYOUT
                }
            )
        ]
    }
]
