##############################################################################################################################################
# 
# Definition of actions for switches DB Version
#
##############################################################################################################################################
 
from pyswitch.hardware.Hardware import Hardware

# from pyswitch.misc import Colors

from pyswitch.clients.kemper import KemperEffectSlot
from pyswitch.controller.ContinuousAction import ContinuousAction
from display import DISPLAY_FOOTER_1, DISPLAY_FOOTER_2, DISPLAY_HEADER_1, DISPLAY_HEADER_2

from pyswitch.clients.kemper.actions.rig_select import RIG_SELECT, RIG_SELECT_DISPLAY_TARGET_RIG
from pyswitch.clients.kemper.actions.bank_select import BANK_SELECT
from pyswitch.clients.kemper.actions.effect_state import EFFECT_STATE
from pyswitch.clients.kemper.actions.morph import MORPH_DISPLAY, MORPH_BUTTON
from pyswitch.clients.kemper.actions.tuner import TUNER_MODE

from pyswitch.clients.kemper.mappings.rig import MAPPING_RIG_VOLUME
from pyswitch.clients.kemper.mappings.morph import MAPPING_MORPH_PEDAL

# Defines the switch assignments and other inputs
Inputs = [
    # Pedal 1
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_EXP_PEDAL_1,
        "actions": [
            ContinuousAction(
                mapping = MAPPING_RIG_VOLUME(),
                auto_calibrate = True
            )
        ]
    },

    # Pedal 2
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_EXP_PEDAL_2,
        "actions": [
            ContinuousAction(
                mapping = MAPPING_MORPH_PEDAL(),
                auto_calibrate = True
            )
        ]
    },

    ####################################################################################

    # Switch 1
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_1,
        "actions": [
            # EFFECT_STATE(
            #     slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A,
            #     display = DISPLAY_HEADER_1
            # ),
            MORPH_DISPLAY(
                display = DISPLAY_HEADER_1
            )
        ],
        "actionsHold": [
            BANK_SELECT(
                bank = 1,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]    
    },

    # Switch 2
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_2,
        "actions": [
            # EFFECT_STATE(
            #     slot_id = KemperEffectSlot.EFFECT_SLOT_ID_B,
            #     display = DISPLAY_HEADER_2          
            # )
            MORPH_BUTTON(
                display = DISPLAY_HEADER_2   
            )
        ],
        "actionsHold": [
            BANK_SELECT(
                bank = 2,
                bank_off = 4,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]    
    },

    # Switch 3
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_3,
        "actions": [
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_DLY,
                display = DISPLAY_FOOTER_1
            )
        ],
        "actionsHold": [
            BANK_SELECT(
                bank = 3,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]    
    },
    
    # Switch 4
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_4,
        "actions": [
                EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_REV,
                display = DISPLAY_FOOTER_2
            )
        ],
        "actionsHold": [
            BANK_SELECT(
                bank = 4,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]    
    },

    # Switch up
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_UP,
        "actions": [
            TUNER_MODE()
        ],
        "actionsHold": [
            BANK_SELECT(
                bank = 5,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]    
    },

    # ########################################################################################

    # Switch A
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_A,
        "actions": [
            RIG_SELECT(
                rig = 1,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                #color = Colors.YELLOW
            ),
            MORPH_DISPLAY()
        ],
        "actionsHold": [
            BANK_SELECT(
                bank = 6,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]    
    },

    # Switch B
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_B,
        "actions": [
            RIG_SELECT(
                rig = 2,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                #color = Colors.BLUE
            ),
            MORPH_DISPLAY()
        ],
        "actionsHold": [
            BANK_SELECT(
                bank = 7,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]    
    },

    # Switch C
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_C,
        "actions": [
            RIG_SELECT(
                rig = 3,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                #color = Colors.ORANGE
            ),
            MORPH_DISPLAY()
        ],
        "actionsHold": [
            BANK_SELECT(
                bank = 8,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]    
    },

    # Switch D
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_D,
        "actions": [
            RIG_SELECT(
                rig = 4,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                #color = Colors.RED
            ),
            MORPH_DISPLAY()
        ],
        "actionsHold": [
            BANK_SELECT(
                bank = 9,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]    
    },

    # Switch down
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_DOWN,
        "actions": [
            RIG_SELECT(
                rig = 5,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                #color = Colors.GREEN
            ),
            MORPH_DISPLAY()
        ],
        "actionsHold": [
            BANK_SELECT(
                bank = 10,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]    
    },
]

