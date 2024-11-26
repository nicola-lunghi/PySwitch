##############################################################################################################################################
# 
# Definition of actions for switches
#
##############################################################################################################################################
 
from pyswitch.hardware.Hardware import Hardware

from pyswitch.misc import Colors
from pyswitch.controller.actions.actions import PushButtonAction, HoldAction

from pyswitch.clients.kemper import KemperActionDefinitions, KemperEffectSlot, KemperMappings
from display import DISPLAY_HEADER_1, DISPLAY_HEADER_2, DISPLAY_FOOTER_1, DISPLAY_FOOTER_2


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
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_B,
                display = DISPLAY_HEADER_2
            )
        ]
    },

    # Switch A
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_A,
        "actions": [
            KemperActionDefinitions.BINARY_SWITCH(
                mapping = KemperMappings.ROTARY_SPEED(
                    slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A
                ),
                display = DISPLAY_FOOTER_1,
                color = Colors.DARK_BLUE,
                text = "A: Fast"
            )
        ]
    },
    
    # Switch B
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_B,
        "actions": [
            KemperActionDefinitions.BINARY_SWITCH(
                mapping = KemperMappings.AMP_STATE(),
                display = DISPLAY_FOOTER_2,
                color = Colors.GRAY,
                text = "Amp"
            )
        ]
    }
]
