from pyswitch.hardware.devices.pa_midicaptain_10 import *
from pyswitch.clients.kemper import KemperEffectSlot
from display import DISPLAY_FOOTER_1, DISPLAY_FOOTER_2, DISPLAY_HEADER_1, DISPLAY_HEADER_2
from pyswitch.clients.kemper.actions.rig_select import RIG_SELECT, RIG_SELECT_DISPLAY_TARGET_RIG
from pyswitch.clients.kemper.actions.bank_select import BANK_SELECT
from pyswitch.clients.kemper.actions.effect_state import EFFECT_STATE
from pyswitch.clients.kemper.actions.morph import MORPH_DISPLAY
from pyswitch.clients.kemper.actions.tuner import TUNER_MODE


Inputs = [

    # Switch 1
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_1,
        "actions": [
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A,
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
        "assignment": PA_MIDICAPTAIN_10_SWITCH_2,
        "actions": [
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_B,
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
        "assignment": PA_MIDICAPTAIN_10_SWITCH_3,
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
        "assignment": PA_MIDICAPTAIN_10_SWITCH_4,
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
        "assignment": PA_MIDICAPTAIN_10_SWITCH_UP,
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
        "assignment": PA_MIDICAPTAIN_10_SWITCH_A,
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
        "assignment": PA_MIDICAPTAIN_10_SWITCH_B,
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
        "assignment": PA_MIDICAPTAIN_10_SWITCH_C,
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
        "assignment": PA_MIDICAPTAIN_10_SWITCH_D,
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
        "assignment": PA_MIDICAPTAIN_10_SWITCH_DOWN,
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
