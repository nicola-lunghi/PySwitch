##############################################################################################################################################
# 
# Definition of actions for switches
#
##############################################################################################################################################
 
from pyswitch.hardware.Hardware import Hardware

from pyswitch.clients.kemper.actions.rig_select import RIG_SELECT, RIG_SELECT_DISPLAY_TARGET_RIG
from pyswitch.clients.kemper.actions.bank_up_down import BANK_UP, BANK_DOWN
from pyswitch.clients.kemper.actions.effect_button import EFFECT_BUTTON


# Defines the switch assignments
Switches = [

    # Switch 1
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_1,
        "actions": [
            RIG_SELECT(
                rig = 4,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]
    },

    # Switch 2
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_2,
        "actions": [
            RIG_SELECT(
                rig = 5,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]
    },

    # Switch 3
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_3,
        "actions": [
            EFFECT_BUTTON(
                num = 2
            )
        ],
        "actionsHold": [
            BANK_UP()
        ]
    },

    # Switch A
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_A,
        "actions": [
            RIG_SELECT(
                rig = 1,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]
    },
    
    # Switch B
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_B,
        "actions": [
            RIG_SELECT(
                rig = 2,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]
    },

    # Switch C
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_C,
        "actions": [
            RIG_SELECT(
                rig = 3,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ],
        "actionsHold": [
            BANK_DOWN()            
        ]
    }
]
