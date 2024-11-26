##############################################################################################################################################
# 
# Definition of actions for switches
#
##############################################################################################################################################
 
from pyswitch.hardware.Hardware import Hardware

from pyswitch.misc import Colors
from pyswitch.controller.actions.actions import HoldAction

from pyswitch.clients.kemper import KemperActionDefinitions, KemperEffectSlot, KemperMappings, RIG_SELECT_DISPLAY_TARGET_RIG
from display import DISPLAY_HEADER_1, DISPLAY_HEADER_2, DISPLAY_FOOTER_1, DISPLAY_FOOTER_2


# Defines the switch assignments
Switches = [

    # Switch 1
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_1,
        "actions": [
            KemperActionDefinitions.RIG_SELECT(
                rig = 1,                
                display = DISPLAY_HEADER_1,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]
    },

    # Switch 2
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_2,
        "actions": [
            KemperActionDefinitions.RIG_SELECT(
                rig = 2,                
                display = DISPLAY_HEADER_2,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]
    },

    # Switch A
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_A,
        "actions": [
            HoldAction({
                "actions": [
                    KemperActionDefinitions.RIG_SELECT(
                        rig = 3,
                        display = DISPLAY_FOOTER_1,
                        display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
                    )
                ],
                "actionsHold": [
                    KemperActionDefinitions.BANK_DOWN(
                        display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
                    )
                ]
            })            
        ]
    },
    
    # Switch B
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_B,
        "actions": [
            HoldAction({
                "actions": [
                    KemperActionDefinitions.RIG_SELECT(
                        rig = 4,
                        display = DISPLAY_FOOTER_2,
                        display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
                    )
                ],
                "actionsHold": [
                    KemperActionDefinitions.BANK_UP(
                        display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
                    )
                ]
            })            
        ]
    }
]
