##############################################################################################################################################
# 
# Definition of actions for switches
#
##############################################################################################################################################
 
from pyswitch.hardware.Hardware import Hardware

from pyswitch.misc import Colors
from pyswitch.controller.actions.actions import PushButtonAction, HoldAction

from pyswitch.clients.kemper import KemperActionDefinitions, KemperEffectSlot, KemperMappings, 
from pyswitch.clients.kemper import RIG_SELECT_DISPLAY_TARGET_RIG, RIG_SELECT_DISPLAY_CURRENT_RIG

from display import DISPLAY_HEADER_1, DISPLAY_HEADER_2, DISPLAY_FOOTER_1, DISPLAY_FOOTER_2


# Defines the switch assignments
Switches = [

    # Switch 1
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_1,
        "actions": [
            KemperActionDefinitions.TUNER_MODE(
                display = DISPLAY_HEADER_1
            )         
        ]
    },

    # Switch 2
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_2,
        "actions": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_X,
                display = DISPLAY_HEADER_2
            )        
        ]
    },

    # Switch A
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_A,
        "actions": [
            KemperActionDefinitions.RIG_SELECT(
                rig = 3,
                rig_off = 1,
                display = DISPLAY_FOOTER_1,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                color = Colors.PINK,
                text = "Synth-3"
            )            
        ]
    },
    
    # Switch B
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_B,
        "actions": [
            KemperActionDefinitions.RIG_SELECT(
                rig = 2,
                rig_off = 1,
                display = DISPLAY_FOOTER_2,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                text = "Lead-2"
            )
        ]
    }
]
