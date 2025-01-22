##############################################################################################################################################
# 
# Definition of actions for switches DB Version
#
##############################################################################################################################################
 
from pyswitch.hardware.Hardware import Hardware

from pyswitch.clients.kemper import KemperEffectSlot
from pyswitch.controller.ContinuousAction import ContinuousAction
from display import DISPLAY_FOOTER_1, DISPLAY_FOOTER_2, DISPLAY_HEADER_1, DISPLAY_HEADER_2, DISPLAY_HEADER_3

from pyswitch.clients.kemper.actions.rig_select import RIG_SELECT_DISPLAY_TARGET_RIG
from pyswitch.clients.kemper.actions.rig_select_and_morph_state import RIG_SELECT_AND_MORPH_STATE
from pyswitch.clients.kemper.actions.effect_state import EFFECT_STATE
from pyswitch.clients.kemper.actions.tuner import TUNER_MODE
from pyswitch.clients.kemper.actions.bank_up_down import BANK_UP, BANK_DOWN

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
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A,
                display = DISPLAY_HEADER_1
            )
        ]    
    },

    # Switch 2
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_2,
        "actions": [
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_B,
                display = DISPLAY_HEADER_2          
            )
        ]    
    },

    # Switch 3
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_3,
        "actions": [
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_C,
                display = DISPLAY_HEADER_3
            )
        ]    
    },
    
    # Switch 4
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_4,
        "actions": [
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_D,
                display = DISPLAY_FOOTER_1
            )
        ],
        "actionsHold": [
            TUNER_MODE()
        ]    
    },

    # Switch up
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_UP,
        "actions": [
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_X,
                display = DISPLAY_FOOTER_2
            )
        ],
        "actionsHold": [
            BANK_UP()
        ]    
    },

    # ########################################################################################

    # Switch A
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_A,
        "actions": RIG_SELECT_AND_MORPH_STATE(
            rig = 1,
            display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
        )    
    },

    # Switch B
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_B,
        "actions": RIG_SELECT_AND_MORPH_STATE(
            rig = 2,
            display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
        )
    },

    # Switch C
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_C,
        "actions": RIG_SELECT_AND_MORPH_STATE(
            rig = 3,
            display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
        )
    },

    # Switch D
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_D,
        "actions": RIG_SELECT_AND_MORPH_STATE(
            rig = 4,
            display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
        )
    },

    # Switch down
    {
        "assignment": Hardware.PA_MIDICAPTAIN_10_SWITCH_DOWN,
        "actions": RIG_SELECT_AND_MORPH_STATE(
            rig = 5,
            display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
        ),
        "actionsHold": [
            BANK_DOWN()
        ]    
    },
]

