##############################################################################################################################################
# 
# Definition of actions for switches
#
##############################################################################################################################################
 
from pyswitch.hardware.Hardware import Hardware

#from pyswitch.misc import Colors

from pyswitch.clients.kemper import KemperActionDefinitions, KemperEffectSlot, RIG_SELECT_DISPLAY_TARGET_RIG #, KemperMappings
from display import DISPLAY_HEADER_1, DISPLAY_HEADER_2, DISPLAY_FOOTER_1, DISPLAY_FOOTER_2


# Defines the switch assignments
Switches = [

    # Switch 1
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_1,
        "actions": [
            KemperActionDefinitions.RIG_SELECT(
                rig = 1,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ],
        "actionsHold": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_C,
                display = DISPLAY_HEADER_1
            )   
        ]    
    },

    # Switch 2
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_2,
        "actions": [
            KemperActionDefinitions.RIG_SELECT(
                rig = 2,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ],
        "actionsHold": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_D,
                display = DISPLAY_HEADER_2
            )
        ]    
    },

    # Switch 3
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_3,
        "actions": [
            KemperActionDefinitions.RIG_SELECT(
                rig = 3,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ],
        "actionsHold": [
            KemperActionDefinitions.TUNER_MODE()
        ]
    },

    # Switch A
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_A,
        "actions": [
            KemperActionDefinitions.RIG_SELECT(
                rig = 4,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ],
        "actionsHold": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_MOD,
                display = DISPLAY_FOOTER_1
            )
        ]    
    },
    
    # Switch B
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_B,
        "actions": [
            KemperActionDefinitions.RIG_SELECT(
                rig = 5,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ],
        "actionsHold": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_DLY,
                display = DISPLAY_FOOTER_2
            )
        ]    
    },

    # Switch C
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_C,
        "actions": [
            KemperActionDefinitions.TAP_TEMPO(use_leds = False),
            KemperActionDefinitions.SHOW_TEMPO()    # Shows beats with the LED(s)
        ]
    }
]
