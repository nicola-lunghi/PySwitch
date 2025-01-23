##############################################################################################################################################
# 
# Definition of actions for switches
#
##############################################################################################################################################
 
from pyswitch.hardware.devices.pa_midicaptain_nano_4 import *

from pyswitch.misc import Colors

from pyswitch.clients.kemper import KemperEffectSlot
from display import DISPLAY_FOOTER_1, DISPLAY_FOOTER_2, DISPLAY_HEADER_1, DISPLAY_HEADER_2

from pyswitch.clients.kemper.actions.tempo import TAP_TEMPO, SHOW_TEMPO
from pyswitch.clients.kemper.actions.tuner import TUNER_MODE
from pyswitch.clients.kemper.actions.morph import MORPH_BUTTON
from pyswitch.clients.kemper.actions.effect_state import EFFECT_STATE


# Defines the switch assignments
Inputs = [

    # Switch 1
    {
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_1,
        "actions": [
            TUNER_MODE(
                display = DISPLAY_HEADER_1
            )                         
        ]
    },

    # Switch 2
    {
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_2,
        "actions": [
            TAP_TEMPO(
                display = DISPLAY_HEADER_2,
                color = Colors.LIGHT_GREEN,
                use_leds = False
            ),
            SHOW_TEMPO()    # Shows beats with the LED(s)   
        ]
    },

    # Switch A
    {
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_A,
        "actions": [
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A,
                display = DISPLAY_FOOTER_1
            )
        ]
    },
    
    # Switch B
    {
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_B,
        "actions": [
            MORPH_BUTTON(
                display = DISPLAY_FOOTER_2,
                #color = "kemper"
            )
        ]
    }
]
