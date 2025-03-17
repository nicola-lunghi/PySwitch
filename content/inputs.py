from pyswitch.hardware.devices.pa_midicaptain_10 import *
from pyswitch.clients.kemper.actions.tempo import TAP_TEMPO
from pyswitch.clients.kemper.actions.tempo import SHOW_TEMPO
from pyswitch.clients.kemper.actions.effect_state import EFFECT_STATE
from pyswitch.clients.kemper.actions.bank_up_down import BANK_UP
from pyswitch.clients.kemper.actions.bank_up_down import BANK_DOWN
from pyswitch.clients.kemper.actions.rig_select import RIG_SELECT
from pyswitch.clients.kemper.actions.tuner import TUNER_MODE
from pyswitch.controller.EncoderAction import EncoderAction
from pyswitch.clients.kemper.actions.rig_select import RIG_SELECT_DISPLAY_TARGET_RIG
from pyswitch.clients.kemper import KemperEffectSlot
from pyswitch.clients.kemper.mappings.amp import MAPPING_AMP_GAIN
from display import DISPLAY_HEADER_1
from display import DISPLAY_HEADER_2
from display import DISPLAY_FOOTER_1
from display import DISPLAY_FOOTER_2

Inputs = [

    # Wheel rotary encoder
    {
        "assignment": PA_MIDICAPTAIN_10_WHEEL_ENCODER, "actions": [
            EncoderAction(
                mapping = MAPPING_AMP_GAIN()
            )
        ]
    },

    # Switch 1
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_1, "actions": [
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A, 
                display = DISPLAY_HEADER_1
            )            
        ]
    },

    # Switch 2
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_2, "actions": [
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_B, 
                display = DISPLAY_HEADER_2
            )
        ]
    },

    # Switch 3
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_3, "actions": [
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_C, 
                display = DISPLAY_FOOTER_1
            )
        ]
    },

    # Switch 4
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_4, "actions": [
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_D, 
                display = DISPLAY_FOOTER_2
            )
        ]
    },

    # Switch Up
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_UP, "actions": [
            TAP_TEMPO(
                use_leds = False
            ),
            SHOW_TEMPO(
                text = 'Tempo'
            )
            
        ], "actionsHold": [
            TUNER_MODE(
                use_leds = False, 
                text = 'Tuner'
            )
        ]
    },

    ############################################################################

    # Switch A
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_A, "actionsHold": [
            BANK_DOWN(
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG, 
                text = 'Bank dn'
            )
            
        ], "actions": [
            RIG_SELECT(
                rig = 1, 
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]
    },
    
    # Switch B
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_B, "actions": [
            RIG_SELECT(
                rig = 2, 
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            ),
            
        ]
    },

    # Switch C
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_C, "actions": [
            RIG_SELECT(
                rig = 3, 
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]
    },

    # Switch D
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_D, "actions": [
            RIG_SELECT(
                rig = 4, 
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]
    },

    # Switch Down
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_DOWN, "actionsHold": [
            BANK_UP(
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG, 
                text = 'Bank up'
            )
            
        ], "actions": [
            RIG_SELECT(
                rig = 5, 
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]
    }
]
