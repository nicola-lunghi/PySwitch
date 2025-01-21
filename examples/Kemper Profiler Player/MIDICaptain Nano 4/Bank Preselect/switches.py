##############################################################################################################################################
# 
# Definition of actions for switches
#
##############################################################################################################################################
 
from pyswitch.hardware.Hardware import Hardware

from pyswitch.clients.kemper.actions.rig_select import RIG_SELECT, RIG_SELECT_DISPLAY_TARGET_RIG
from pyswitch.clients.kemper.actions.bank_select import BANK_SELECT

from display import DISPLAY_HEADER_1, DISPLAY_HEADER_2, DISPLAY_FOOTER_1, DISPLAY_FOOTER_2

##############################################################################################################################################

# Defines the switch assignments
Switches = [

    # Switch 1
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_1,
        "actions": [
            BANK_SELECT(
                bank = 1,
                preselect = True,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                display = DISPLAY_HEADER_1
            )         
        ]
    },

    # Switch 2
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_2,
        "actions": [
            BANK_SELECT(
                bank = 2,
                preselect = True,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                display = DISPLAY_HEADER_2
            )     
        ]
    },

    # Switch A
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_A,
        "actions": [
            RIG_SELECT(
                rig = 2,
                rig_off = 1,
                display = DISPLAY_FOOTER_1,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG                
            )   
        ]
    },
    
    # Switch B
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_B,
        "actions": [
            RIG_SELECT(
                rig = 3,
                rig_off = 1,
                display = DISPLAY_FOOTER_2,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]
    },
]
