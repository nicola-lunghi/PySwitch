##############################################################################################################################################
# 
# Definition of actions for switches DB Version
#
##############################################################################################################################################
 
from pyswitch.hardware.Hardware import Hardware

#from pyswitch.misc import Colors

from pyswitch.clients.kemper import KemperActionDefinitions, KemperEffectSlot, RIG_SELECT_DISPLAY_TARGET_RIG
from display import DISPLAY_FOOTER_1, DISPLAY_FOOTER_2, DISPLAY_HEADER_1, DISPLAY_HEADER_2

# Defines the switch assignments
Switches = [

    # Switch 1
    {
       "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_1,
        "actions": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A,
                
            )
        ],
        "actionsHold": [
            KemperActionDefinitions.BANK_SELECT(
                bank = 1,
                display = DISPLAY_HEADER_1,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]    
    },

    # Switch 2
    {
       "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_2,
        "actions": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_B,
                
            )
        ],
        "actionsHold": [
            KemperActionDefinitions.BANK_SELECT(
                bank = 2,
                bank_off = 4,
                display = DISPLAY_HEADER_2,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]    
    },

    # Switch 3
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_3,
        "actions": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_DLY,
                display = DISPLAY_FOOTER_1
            )
        ],
        "actionsHold": [
            KemperActionDefinitions.BANK_SELECT(
                bank = 3,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]    
    },
    
    # Switch 4
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_4,
        "actions": [
                KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_REV,
                display = DISPLAY_FOOTER_2
            )
        ],
        "actionsHold": [
            KemperActionDefinitions.BANK_SELECT(
                bank = 4,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]    
    },

    # Switch up
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_UP,
        "actions": [
            KemperActionDefinitions.TUNER_MODE()
        ],
        "actionsHold": [
            KemperActionDefinitions.BANK_SELECT(
                bank = 5,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]    
    },

    ########################################################################################

    # Switch A
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_A,
        "actions": [
            KemperActionDefinitions.RIG_SELECT(
                rig = 1,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                #color = Colors.YELLOW
            ),
            KemperActionDefinitions.MORPH_DISPLAY()
        ],
        "actionsHold": [
            KemperActionDefinitions.BANK_SELECT(
                bank = 6,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]    
    },

    # Switch B
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_B,
        "actions": [
            KemperActionDefinitions.RIG_SELECT(
                rig = 2,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                #color = Colors.BLUE
            ),
            KemperActionDefinitions.MORPH_DISPLAY()
        ],
        "actionsHold": [
            KemperActionDefinitions.BANK_SELECT(
                bank = 7,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]    
    },

    # Switch C
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_C,
        "actions": [
            KemperActionDefinitions.RIG_SELECT(
                rig = 3,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                #color = Colors.ORANGE
            ),
            KemperActionDefinitions.MORPH_DISPLAY()
        ],
        "actionsHold": [
            KemperActionDefinitions.BANK_SELECT(
                bank = 8,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]    
    },

    # Switch D
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_D,
        "actions": [
            KemperActionDefinitions.RIG_SELECT(
                rig = 4,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                #color = Colors.RED
            ),
            KemperActionDefinitions.MORPH_DISPLAY()
        ],
        "actionsHold": [
            KemperActionDefinitions.BANK_SELECT(
                bank = 9,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]    
    },

    # Switch down
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_DOWN,
        "actions": [
            KemperActionDefinitions.RIG_SELECT(
                rig = 5,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                #color = Colors.GREEN
            ),
            KemperActionDefinitions.MORPH_DISPLAY()
        ],
        "actionsHold": [
            KemperActionDefinitions.BANK_SELECT(
                bank = 10,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]    
    },
]
