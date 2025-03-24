from pyswitch.clients.kemper.actions.tempo import TAP_TEMPO
from pyswitch.clients.kemper.actions.tempo import SHOW_TEMPO
from pyswitch.clients.kemper.actions.effect_state_extended_names import EFFECT_STATE_EXT
from pyswitch.clients.kemper.actions.tuner import TUNER_MODE
from pyswitch.clients.kemper import KemperEffectSlot
from display import DISPLAY_HEADER_1
from display import DISPLAY_HEADER_2
from display import DISPLAY_FOOTER_1
from display import DISPLAY_FOOTER_2
from pyswitch.hardware.devices.pa_midicaptain_nano_4 import *


Inputs = [
    {
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_1,
        "actions": [
            EFFECT_STATE_EXT(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_C, 
                display = DISPLAY_HEADER_1
            ),
            
        ],
        "actionsHold": [],
        
    },
    {
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_2,
        "actions": [
            TAP_TEMPO(
                use_leds = False
            ),
            SHOW_TEMPO(
                text = 'Tempo'
            ),
            
        ],
        "actionsHold": [
            TUNER_MODE(
                display = DISPLAY_HEADER_2, 
                text = 'Tuner'
            ),
            
        ],
        
    },
    {
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_A,
        "actions": [
            EFFECT_STATE_EXT(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_B, 
                display = DISPLAY_FOOTER_1
            ),
            
        ],
        "actionsHold": [],
        
    },
    {
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_B,
        "actions": [
            EFFECT_STATE_EXT(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_MOD, 
                display = DISPLAY_FOOTER_2
            ),
            
        ],
        "actionsHold": [],
        
    },
    
]
