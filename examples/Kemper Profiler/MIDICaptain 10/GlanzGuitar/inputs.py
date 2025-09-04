##############################################################################################################################################
# 
# Definition of actions for switches DB Version
#
##############################################################################################################################################
 
from pyswitch.clients.kemper.actions.morph import MORPH_BUTTON
from pyswitch.clients.kemper.actions.effect_state import EFFECT_STATE
from pyswitch.clients.kemper.actions.rig_select import RIG_SELECT
from pyswitch.clients.kemper.actions.bank_select import BANK_SELECT
from pyswitch.controller.actions.AnalogAction import AnalogAction
from pyswitch.clients.local.actions.pager import PagerAction
from pyswitch.colors import Colors
from pyswitch.clients.kemper.actions.rig_select import RIG_SELECT_DISPLAY_TARGET_RIG
from pyswitch.clients.kemper import KemperEffectSlot
from pyswitch.clients.kemper.mappings.pedals import MAPPING_WAH_PEDAL
from display import DISPLAY_HEADER_1
from display import DISPLAY_HEADER_2
from display import DISPLAY_HEADER_3
from display import DISPLAY_HEADER_4
from display import DISPLAY_FOOTER_1
from display import DISPLAY_FOOTER_2
from display import DISPLAY_FOOTER_3
from display import DISPLAY_FOOTER_4
from pyswitch.hardware.devices.pa_midicaptain_10 import *

_pager = PagerAction(
    pages = [
        {
            "id": 1,
            "color": Colors.WHITE,
            "text": 'FX only',
            
        },
        {
            "id": 2,
            "color": Colors.RED,
            "text": 'Bank+Rig+FX',
            
        },
        
    ]
)



##############################################################################################################################################

# Defines the switch assignments and other inputs
Inputs = [
    {
        "assignment": PA_MIDICAPTAIN_10_EXP_PEDAL_1,
        "actions": [],
        
    },
    {
        "assignment": PA_MIDICAPTAIN_10_EXP_PEDAL_2,
        "actions": [
            AnalogAction(
                mapping = MAPPING_WAH_PEDAL(), 
                auto_calibrate = True
            ),
            
        ],
        
    },
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_1,
        "actionsHold": [
            BANK_SELECT(
                bank = 1, 
                preselect = True, 
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG, 
                id = 2, 
                enable_callback = _pager.enable_callback
            ),
            
        ],
        "actions": [
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_X, 
                display = DISPLAY_HEADER_1, 
                id = 1, 
                enable_callback = _pager.enable_callback
            ),
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_X, 
                display = DISPLAY_HEADER_1, 
                id = 2, 
                enable_callback = _pager.enable_callback
            ),
            
        ],
        
    },
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_2,
        "actionsHold": [
            BANK_SELECT(
                bank = 2, 
                preselect = True, 
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG, 
                id = 2, 
                enable_callback = _pager.enable_callback
            ),
            
        ],
        "actions": [
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_MOD, 
                display = DISPLAY_HEADER_2, 
                id = 1, 
                enable_callback = _pager.enable_callback
            ),
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_MOD, 
                display = DISPLAY_HEADER_2, 
                id = 2, 
                enable_callback = _pager.enable_callback
            ),
            
        ],
        
    },
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_3,
        "actionsHold": [
            BANK_SELECT(
                bank = 3, 
                preselect = True, 
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG, 
                id = 2, 
                enable_callback = _pager.enable_callback
            ),
            
        ],
        "actions": [
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_DLY, 
                display = DISPLAY_HEADER_3, 
                id = 1, 
                enable_callback = _pager.enable_callback
            ),
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_DLY, 
                display = DISPLAY_HEADER_3, 
                id = 2, 
                enable_callback = _pager.enable_callback
            ),
            
        ],
        
    },
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_4,
        "actionsHold": [
            BANK_SELECT(
                bank = 4, 
                preselect = True, 
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG, 
                id = 2, 
                enable_callback = _pager.enable_callback
            ),
            
        ],
        "actions": [
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_REV, 
                display = DISPLAY_HEADER_4, 
                id = 1, 
                enable_callback = _pager.enable_callback
            ),
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_REV, 
                display = DISPLAY_HEADER_4, 
                id = 2, 
                enable_callback = _pager.enable_callback
            ),
            
        ],
        
    },
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_UP,
        "actions": [
            _pager,
            
        ],
        "actionsHold": [
            BANK_SELECT(
                bank = 5, 
                preselect = True, 
                id = 2, 
                enable_callback = _pager.enable_callback
            ),
            
        ],
        
    },
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_A,
        "actionsHold": [
            RIG_SELECT(
                rig = 1, 
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG, 
                id = 2, 
                enable_callback = _pager.enable_callback
            ),
            
        ],
        "actions": [
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A, 
                display = DISPLAY_FOOTER_1, 
                id = 1, 
                enable_callback = _pager.enable_callback
            ),
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A, 
                display = DISPLAY_FOOTER_1, 
                id = 2, 
                enable_callback = _pager.enable_callback
            ),
            
        ],
        
    },
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_B,
        "actionsHold": [
            RIG_SELECT(
                rig = 2, 
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG, 
                id = 2, 
                enable_callback = _pager.enable_callback
            ),
            
        ],
        "actions": [
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_B, 
                display = DISPLAY_FOOTER_2, 
                id = 1, 
                enable_callback = _pager.enable_callback
            ),
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_B, 
                display = DISPLAY_FOOTER_2, 
                id = 2, 
                enable_callback = _pager.enable_callback
            ),
            
        ],
        
    },
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_C,
        "actionsHold": [
            RIG_SELECT(
                rig = 3, 
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG, 
                id = 2, 
                enable_callback = _pager.enable_callback
            ),
            
        ],
        "actions": [
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_C, 
                display = DISPLAY_FOOTER_3, 
                id = 1, 
                enable_callback = _pager.enable_callback
            ),
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_C, 
                display = DISPLAY_FOOTER_3, 
                id = 2, 
                enable_callback = _pager.enable_callback
            ),
            
        ],
        
    },
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_D,
        "actionsHold": [
            RIG_SELECT(
                rig = 4, 
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG, 
                id = 2, 
                enable_callback = _pager.enable_callback
            ),
            
        ],
        "actions": [
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_D, 
                display = DISPLAY_FOOTER_4, 
                id = 1, 
                enable_callback = _pager.enable_callback
            ),
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_D, 
                display = DISPLAY_FOOTER_4, 
                id = 2, 
                enable_callback = _pager.enable_callback
            ),
            
        ],
        
    },
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_DOWN,
        "actionsHold": [
            RIG_SELECT(
                rig = 5, 
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG, 
                id = 2, 
                enable_callback = _pager.enable_callback
            ),
            
        ],
        "actions": [
            MORPH_BUTTON(
                text = 'Morph', 
                morph_color_base = Colors.BLUE, 
                morph_color_morphed = Colors.RED
            ),
            
        ],
        
    },
    
]
