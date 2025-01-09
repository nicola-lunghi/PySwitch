##############################################################################################################################################
# 
# Definition of actions for switches
#
##############################################################################################################################################
 
from pyswitch.hardware.Hardware import Hardware
from pyswitch.clients.kemper import KemperActionDefinitions, RIG_SELECT_DISPLAY_TARGET_RIG


# Defines the switch assignments
Switches = [

    # Switch 1
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_1,
        "actions": [
            KemperActionDefinitions.RIG_SELECT(
                rig = 4,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]
    },

    # Switch 2
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_2,
        "actions": [
            KemperActionDefinitions.RIG_SELECT(
                rig = 5,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]
    },

    # Switch 3
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_3,
        "actions": [
            KemperActionDefinitions.EFFECT_BUTTON(
                num = 2
            )
        ],
        "actionsHold": [
            KemperActionDefinitions.BANK_UP()
        ]
    },

    # Switch A
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_A,
        "actions": [
            KemperActionDefinitions.RIG_SELECT(
                rig = 1,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]
    },
    
    # Switch B
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_B,
        "actions": [
            KemperActionDefinitions.RIG_SELECT(
                rig = 2,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]
    },

    # Switch C
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_C,
        "actions": [
            KemperActionDefinitions.RIG_SELECT(
                rig = 3,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ],
        "actionsHold": [
            KemperActionDefinitions.BANK_DOWN()            
        ]
    }
]
