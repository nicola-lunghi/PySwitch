##############################################################################################################################################
# 
# Definition of actions for switches
#
##############################################################################################################################################
 
from pyswitch.hardware.devices.pa_midicaptain_nano_4 import *

from pyswitch.misc import Colors

from pyswitch.clients.kemper import KemperEffectSlot
from display import DISPLAY_HEADER_1, DISPLAY_HEADER_2, DISPLAY_FOOTER_1, DISPLAY_FOOTER_2

from pyswitch.clients.kemper.actions.tempo import TAP_TEMPO, SHOW_TEMPO
from pyswitch.clients.kemper.actions.tuner import TUNER_MODE
from pyswitch.clients.kemper.actions.binary_switch import BINARY_SWITCH
from pyswitch.clients.kemper.actions.rig_select import RIG_SELECT, RIG_SELECT_DISPLAY_TARGET_RIG

from pyswitch.clients.kemper.mappings.freeze import MAPPING_FREEZE

##############################################################################################################################################

# Defines the switch assignments
Inputs = [

    # Switch 1
    {
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_1,
        "actions": [
            TAP_TEMPO(use_leds = False),
            SHOW_TEMPO()    # Shows beats with the LED(s)
        ],
        "actionsHold": [
            TUNER_MODE(
                display = DISPLAY_HEADER_1,
                text = "Tap|Tune"
            )            
        ]
    },

    # Switch 2
    {
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_2,
        "actions": [
            # Freeze on/off
            BINARY_SWITCH(
                mapping = MAPPING_FREEZE(KemperEffectSlot.EFFECT_SLOT_ID_DLY),
                display = DISPLAY_HEADER_2,
                text = "Freeze",
                color = Colors.LIGHT_GREEN
            )
        ]
    },

    # Switch A
    {
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_A,
        "actions": [
            RIG_SELECT(
                rig = 4,
                rig_off = "auto",
                auto_exclude_rigs = (4, 5),
                display = DISPLAY_FOOTER_1,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                color = Colors.PINK,
                text = "Synth-4"
            )   
        ]
    },
    
    # Switch B
    {
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_B,
        "actions": [
            RIG_SELECT(
                rig = 5,
                rig_off = "auto",
                auto_exclude_rigs = (4, 5),
                display = DISPLAY_FOOTER_2,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                color = Colors.RED,
                text = "Lead-5"
            )
        ]
    },
]
