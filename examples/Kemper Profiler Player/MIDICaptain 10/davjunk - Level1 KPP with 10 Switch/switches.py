##############################################################################################################################################
# 
# Definition of actions for switches DB Version
#
##############################################################################################################################################
 
from pyswitch.hardware.Hardware import Hardware

#from pyswitch.misc import Colors

from pyswitch.clients.kemper import KemperActionDefinitions, KemperEffectSlot, RIG_SELECT_DISPLAY_TARGET_RIG
from pyswitch.controller.actions.actions import HoldAction
from display import DISPLAY_FOOTER_1, DISPLAY_FOOTER_2, DISPLAY_HEADER_1, DISPLAY_HEADER_2

# Defines the switch assignments
Switches = [

    # Switch 1
    {
       "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_1,
        "actions": [
            HoldAction({
                "actions": [
                    KemperActionDefinitions.EFFECT_STATE(
                        slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A,
                        display = DISPLAY_HEADER_1
                    )
                ],
                "actionsHold": [
                    KemperActionDefinitions.RIG_AND_BANK_SELECT(
                        rig = 1,               
                        bank = 1,
                        use_leds = False,                
                        display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
                    )
                ]    
            }) 
        ]
    },

    # Switch 2
       {
       "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_2,
        "actions": [
            HoldAction({
                "actions": [
                    KemperActionDefinitions.EFFECT_STATE(
                        slot_id = KemperEffectSlot.EFFECT_SLOT_ID_B,
                        display = DISPLAY_HEADER_2
                    )
                ],
                "actionsHold": [
                    KemperActionDefinitions.RIG_AND_BANK_SELECT(
                        rig = 1,               
                        bank = 2,
                        use_leds = False,
                        display_mode = RIG_SELECT_DISPLAY_TARGET_RIG

                    )
                ]    
            }) 
        ]
    },

    # Switch 3
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_3,
        "actions": [
            HoldAction({
                "actions": [
                    KemperActionDefinitions.EFFECT_STATE(
                        slot_id = KemperEffectSlot.EFFECT_SLOT_ID_DLY,
                        display = DISPLAY_FOOTER_1
                    )
                ],
                "actionsHold": [
                    KemperActionDefinitions.RIG_AND_BANK_SELECT(
                        rig = 1,               
                        bank = 3,
                        use_leds = False,
                        display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
                    )
                ]    
            }) 
        ]
    },
    
    # Switch 4
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_4,
        "actions": [
            HoldAction({
                "actions": [
                     KemperActionDefinitions.EFFECT_STATE(
                        slot_id = KemperEffectSlot.EFFECT_SLOT_ID_REV,
                        display = DISPLAY_FOOTER_2
                    )
                ],
                "actionsHold": [
                    KemperActionDefinitions.RIG_AND_BANK_SELECT(
                        rig = 1,               
                        bank = 4,
                        use_leds = False,
                        display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
                    )
                ]    
            }) 
        ]
    },

    # Switch up
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_UP,
        "actions": [
            HoldAction({
                "actions": [
                    KemperActionDefinitions.TUNER_MODE()
                ],
                "actionsHold": [
                    KemperActionDefinitions.RIG_AND_BANK_SELECT(
                        rig = 1,               
                        bank = 5,
                        use_leds = False,
                        display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
                    )
                ]    
            }) 
        ]
    },

    # Switch A
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_A,
        "actions": [
            HoldAction({
                "actions": [
                    KemperActionDefinitions.RIG_SELECT(
                        rig = 1,
                        display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
                    )
                ],
                "actionsHold": [
                    KemperActionDefinitions.RIG_AND_BANK_SELECT(
                        rig = 1,               
                        bank = 6,
                        use_leds = False,
                        display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
                    )
                ]    
            }) 
        ]
    },

    # Switch B
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_B,
        "actions": [
            HoldAction({
                "actions": [
                    KemperActionDefinitions.RIG_SELECT(
                        rig = 2,
                        display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
                    )
                ],
                "actionsHold": [
                    KemperActionDefinitions.RIG_AND_BANK_SELECT(
                        rig = 1,               
                        bank = 7,
                        use_leds = False,
                        display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
                    )
                ]    
            }) 
        ]
    },

    # Switch C
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_C,
        "actions": [
            HoldAction({
                "actions": [
                    KemperActionDefinitions.RIG_SELECT(
                        rig = 3,
                        display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
                    )
                ],
                "actionsHold": [
                    KemperActionDefinitions.RIG_AND_BANK_SELECT(
                        rig = 1,               
                        bank = 8,
                        use_leds = False,
                        display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
                    )
                ]    
            }) 
        ]
    },

    # Switch D
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_D,
        "actions": [
            HoldAction({
                "actions": [
                    KemperActionDefinitions.RIG_SELECT(
                        rig = 4,
                        display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
                    )
                ],
                "actionsHold": [
                    KemperActionDefinitions.RIG_AND_BANK_SELECT(
                        rig = 1,               
                        bank = 9,
                        use_leds = False,
                        display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
                    )
                ]    
            }) 
        ]
    },

    # Switch down
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_DOWN,
        "actions": [
            HoldAction({
                "actions": [
                    KemperActionDefinitions.RIG_SELECT(
                        rig = 5,
                        display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
                    )
                ],
                "actionsHold": [
                    KemperActionDefinitions.RIG_AND_BANK_SELECT(
                        rig = 1,               
                        bank = 10,
                        use_leds = False,
                        display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
                    )
                ]    
            }) 
        ]
    },
]
