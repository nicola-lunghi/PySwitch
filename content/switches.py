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
        "assignment": SwitchDefinitions.PA_MIDICAPTAIN_MINI_SWITCH_1,
        "actions": HoldAction({
            "actions": KemperActionDefinitions.RIG_SELECT(
                rig = 1,
                color = Colors.YELLOW
            ),
            "actionsHold": KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_C,
                display = {
                    "id": DisplayIds.DISPLAY_HEADER,
                    "index": 0,
                    "layout": ACTION_LABEL_LAYOUT
                }
            )       
        }) 
    },

    # Switch 2
    {
        "assignment": SwitchDefinitions.PA_MIDICAPTAIN_MINI_SWITCH_2,
        "actions": HoldAction({
            "actions": KemperActionDefinitions.RIG_SELECT(
                rig = 2,
                color = Colors.YELLOW
            ),
            "actionsHold": KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_D,
                display = {
                    "id": DisplayIds.DISPLAY_HEADER,
                    "index": 1,
                    "layout": ACTION_LABEL_LAYOUT
                }
            )       
        }) 
    },

    # Switch 3
    {
        "assignment": SwitchDefinitions.PA_MIDICAPTAIN_MINI_SWITCH_3,
        "actions": HoldAction({
            "actions": KemperActionDefinitions.RIG_SELECT(
                rig = 3,
                color = Colors.YELLOW
            ),
            "actionsHold": KemperActionDefinitions.TUNER_MODE()
        }) 
    },

    # Switch A
    {
        "assignment": SwitchDefinitions.PA_MIDICAPTAIN_MINI_SWITCH_A,
        "actions": HoldAction({
            "actions": KemperActionDefinitions.RIG_SELECT(
                rig = 4,
                color = Colors.YELLOW
            ),
            "actionsHold": KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_MOD,
                display = {
                    "id": DisplayIds.DISPLAY_FOOTER,
                    "index": 0,
                    "layout": ACTION_LABEL_LAYOUT
                }
            )       
        }) 
    },
    
    # Switch B
    {
        "assignment": SwitchDefinitions.PA_MIDICAPTAIN_MINI_SWITCH_B,
        "actions": HoldAction({
            "actions": KemperActionDefinitions.RIG_SELECT(
                rig = 5,
                color = Colors.YELLOW
            ),
            "actionsHold": KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_DLY,
                display = {
                    "id": DisplayIds.DISPLAY_FOOTER,
                    "index": 1,
                    "layout": ACTION_LABEL_LAYOUT
                }
            )       
        }) 
    },

    # Switch C
    {
        "assignment": SwitchDefinitions.PA_MIDICAPTAIN_MINI_SWITCH_C,
        "actions": KemperActionDefinitions.TAP_TEMPO()
    }
]
