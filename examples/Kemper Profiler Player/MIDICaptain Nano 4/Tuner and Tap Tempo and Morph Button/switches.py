##############################################################################################################################################
# 
# Definition of actions for switches
#
##############################################################################################################################################
 
from pyswitch.hardware.Hardware import Hardware

from pyswitch.misc import Colors

from pyswitch.clients.kemper import KemperActionDefinitions, KemperEffectSlot, KemperMappings
from display import DISPLAY_FOOTER_1, DISPLAY_FOOTER_2, DISPLAY_HEADER_1, DISPLAY_HEADER_2

# Defines the switch assignments
Switches = [

    # Switch 1
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_1,
        "actions": [
            KemperActionDefinitions.TUNER_MODE(
                display = DISPLAY_HEADER_1
            )                         
        ]
    },

    # Switch 2
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_2,
        "actions": [
            KemperActionDefinitions.TAP_TEMPO(
                display = DISPLAY_HEADER_2,
                color = Colors.LIGHT_GREEN,
                use_leds = False
            ),
            KemperActionDefinitions.SHOW_TEMPO()    # Shows beats with the LED(s)   
        ]
    },

    # Switch A
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_A,
        "actions": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A,
                display = DISPLAY_FOOTER_1
            )
        ]
    },
    
    # Switch B
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_B,
        "actions": [
            KemperActionDefinitions.MORPH_BUTTON(
                display = DISPLAY_FOOTER_2
            )
        ]
    }
]
