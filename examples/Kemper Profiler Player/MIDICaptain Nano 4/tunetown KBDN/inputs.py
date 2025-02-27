from pyswitch.hardware.devices.pa_midicaptain_nano_4 import *
from pyswitch.misc import Colors
from pyswitch.clients.kemper import KemperEffectSlot
from display import DISPLAY_HEADER_1, DISPLAY_HEADER_2, DISPLAY_FOOTER_1, DISPLAY_FOOTER_2
from pyswitch.clients.kemper.actions.morph import MORPH_DISPLAY
from pyswitch.clients.kemper.actions.tuner import TUNER_MODE
from pyswitch.clients.kemper.actions.effect_state import EFFECT_STATE
from pyswitch.clients.kemper.actions.rig_select import RIG_SELECT, RIG_SELECT_DISPLAY_TARGET_RIG


Inputs = [

    # Switch 1
    {
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_1,
        "actions": [
            TUNER_MODE(
                display = DISPLAY_HEADER_1
            ),
            MORPH_DISPLAY()        
        ]
    },

    # Switch 2
    {
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_2,
        "actions": [   
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_X,
                display = DISPLAY_HEADER_2
            )
        ]               
    },

    # Switch A
    {
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_A,
        "actions": [
            RIG_SELECT(
                rig = 3,
                rig_off = 1,
                display = DISPLAY_FOOTER_1,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                color = Colors.PINK,
                text = "Synth-3"
            )            
        ]
    },
    
    # Switch B
    {
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_B,
        "actions": [
            RIG_SELECT(
                rig = 2,
                rig_off = 1,
                display = DISPLAY_FOOTER_2,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                text = "Lead-2"
            )
        ]
    }
]
