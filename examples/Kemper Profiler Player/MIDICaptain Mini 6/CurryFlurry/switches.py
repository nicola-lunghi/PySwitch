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

# Defines the switch assignments
Switches = [

    # Switch 1
    {
        "assignment": SwitchDefinitions.PA_MIDICAPTAIN_MINI_SWITCH_1,
        "actions": [
            KemperActionDefinitions.RIG_SELECT(
                rig = 4,
                color = Colors.YELLOW
            )  
        ]
    },

    # Switch 2
    {
        "assignment": SwitchDefinitions.PA_MIDICAPTAIN_MINI_SWITCH_2,
        "actions": [
            KemperActionDefinitions.RIG_SELECT(
                rig = 5,
                color = Colors.YELLOW
            )  
        ]
    },

    # Switch 3
    {
        "assignment": SwitchDefinitions.PA_MIDICAPTAIN_MINI_SWITCH_3,
        "actions": [
            HoldAction({
                "actions": KemperActionDefinitions.EFFECT_BUTTON(
                    num = 2
                ),
                "actionsHold": KemperActionDefinitions.BANK_UP()
            })            
        ]
    },

    # Switch A
    {
        "assignment": SwitchDefinitions.PA_MIDICAPTAIN_MINI_SWITCH_A,
        "actions": [
            KemperActionDefinitions.RIG_SELECT(
                rig = 1,
                color = Colors.YELLOW
            )   
        ]
    },
    
    # Switch B
    {
        "assignment": SwitchDefinitions.PA_MIDICAPTAIN_MINI_SWITCH_B,
        "actions": [
               KemperActionDefinitions.RIG_SELECT(
                rig = 2,
                color = Colors.YELLOW
            )   
        ]
    },

    # Switch C
    {
        "assignment": SwitchDefinitions.PA_MIDICAPTAIN_MINI_SWITCH_C,
        "actions": [
            HoldAction({
                "actions": KemperActionDefinitions.RIG_SELECT(
                    rig = 3,
                    color = Colors.YELLOW
                ),
                "actionsHold": KemperActionDefinitions.BANK_DOWN()
            })
        ]
    }
]
