from pyswitch.clients.kemper.actions.morph import MORPH_DISPLAY
from pyswitch.clients.kemper.actions.rig_select import RIG_SELECT
from pyswitch.clients.kemper.actions.tuner import TUNER_MODE
from pyswitch.colors import Colors
from pyswitch.clients.kemper.actions.rig_select import RIG_SELECT_DISPLAY_TARGET_RIG
from display import DISPLAY_HEADER_1
from display import DISPLAY_HEADER_2
from display import DISPLAY_FOOTER_1
from display import DISPLAY_FOOTER_2
from pyswitch.hardware.devices.pa_midicaptain_nano_4 import *


Inputs = [
    {
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_1,
        "actions": [
            TUNER_MODE(
                display = DISPLAY_HEADER_1, 
                use_leds = False
            ),
            MORPH_DISPLAY(),
            
        ],
        
    },
    {
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_2,
        "actions": [
            RIG_SELECT(
                rig = 4, 
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG, 
                display = DISPLAY_HEADER_2, 
                rig_off = 1, 
                color = (0, 213, 255), 
                text = 'L7'
            ),
            
        ],
        
    },
    {
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_A,
        "actions": [
            RIG_SELECT(
                rig = 3, 
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG, 
                display = DISPLAY_FOOTER_1, 
                rig_off = 1, 
                color = Colors.PINK, 
                text = 'Synth 3'
            ),
            
        ],
        
    },
    {
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_B,
        "actions": [
            RIG_SELECT(
                rig = 2, 
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG, 
                display = DISPLAY_FOOTER_2, 
                rig_off = 1, 
                text = 'Lead 2'
            ),
            
        ],
        
    },
    
]
