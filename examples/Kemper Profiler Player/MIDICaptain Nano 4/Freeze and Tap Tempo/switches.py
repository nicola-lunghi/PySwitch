##############################################################################################################################################
# 
# Definition of actions for switches
#
##############################################################################################################################################
 
from pyswitch.hardware.Hardware import Hardware

from pyswitch.misc import Colors
from pyswitch.controller.actions.actions import PushButtonAction, HoldAction
from pyswitch.controller.callbacks import BinaryParameterCallback

from pyswitch.clients.kemper import KemperActionDefinitions, KemperEffectSlot, KemperMappings
from display import DISPLAY_HEADER_1, DISPLAY_HEADER_2, DISPLAY_FOOTER_1, DISPLAY_FOOTER_2


# Defines the switch assignments
Switches = [

    # Switch 1
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_1,
        "actions": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A,
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
            PushButtonAction({
                "callback": BinaryParameterCallback(
                    mapping = KemperMappings.FREEZE(KemperEffectSlot.EFFECT_SLOT_ID_REV),
                    text = "RvFreeze",
                    color = Colors.DARK_GREEN
                ),
                "mode": PushButtonAction.MOMENTARY,
                "display": DISPLAY_FOOTER_1,
                "useSwitchLeds": True
            })
        ]
    },
    
    # Switch B
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_B,
        "actions": [
            KemperActionDefinitions.TAP_TEMPO(
                display = DISPLAY_FOOTER_2,
                color = Colors.LIGHT_GREEN,
                use_leds = False
            ),
            KemperActionDefinitions.SHOW_TEMPO()    # Shows beats with the LED(s)
        ]
    }
]
