from pyswitch.hardware.devices.pa_midicaptain_nano_4 import *
from pyswitch.misc import Colors
from pyswitch.controller.actions import PushButtonAction
from pyswitch.controller.callbacks import BinaryParameterCallback
from pyswitch.clients.kemper import KemperEffectSlot
from display import DISPLAY_HEADER_1, DISPLAY_HEADER_2, DISPLAY_FOOTER_1, DISPLAY_FOOTER_2
from pyswitch.clients.kemper.actions.tempo import TAP_TEMPO, SHOW_TEMPO
from pyswitch.clients.kemper.actions.effect_state import EFFECT_STATE
from pyswitch.clients.kemper.mappings.freeze import MAPPING_FREEZE


Inputs = [

    # Switch 1
    {
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_1,
        "actions": [
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A,
                display = DISPLAY_HEADER_1
            )                         
        ]
    },

    # Switch 2
    {
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_2,
        "actions": [
            EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_B,
                display = DISPLAY_HEADER_2
            )
        ]
    },

    # Switch A
    {
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_A,
        "actions": [
            PushButtonAction({
                "callback": BinaryParameterCallback(
                    mapping = MAPPING_FREEZE(KemperEffectSlot.EFFECT_SLOT_ID_REV),
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
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_B,
        "actions": [
            TAP_TEMPO(
                display = DISPLAY_FOOTER_2,
                color = Colors.LIGHT_GREEN,
                use_leds = False
            ),
            SHOW_TEMPO()
        ]
    }
]
