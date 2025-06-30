from pyswitch.clients.kemper.actions.rig_volume_boost import RIG_VOLUME_BOOST
from pyswitch.clients.kemper.actions.tempo import TAP_TEMPO
from pyswitch.clients.kemper.actions.tempo import SHOW_TEMPO
from pyswitch.clients.kemper.actions.effect_state_extended_names import EFFECT_STATE_EXT
from pyswitch.clients.kemper.actions.tuner import TUNER_MODE
from pyswitch.colors import Colors
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
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_MOD, 
                display = DISPLAY_HEADER_1
            ),
            
        ],
        "actionsHold": [],
        
    },
    {
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_2,
        "actions": [
            TAP_TEMPO(),
            SHOW_TEMPO(
                text = '{bpm} bpm'
            ),
            
        ],
        "actionsHold": [
            TUNER_MODE(
                display = DISPLAY_HEADER_2, 
                use_leds = False, 
                text = 'Tap|Tuner'
            ),
            
        ],
        
    },
    {
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_A,
        "actions": [
            EFFECT_STATE_EXT(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_X, 
                display = DISPLAY_FOOTER_1, 
                text = 'Slap'
            ),
            
        ],
        "actionsHold": [],
        
    },
    {
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_B,
        "actions": [
            RIG_VOLUME_BOOST(
                boost_volume = 0.75, 
                display = DISPLAY_FOOTER_2, 
                color = Colors.RED, 
                text = '+6 dB'
            ),
            
        ],
        
    },
    
]
