##############################################################################################################################################
# 
# Definition of actions for switches
#
##############################################################################################################################################
 
from pyswitch.hardware.Hardware import Hardware

from pyswitch.misc import DEFAULT_LABEL_COLOR, Colors
from pyswitch.controller.actions.actions import HoldAction, ParameterAction, PushButtonAction
#from pyswitch.controller.ConditionTree import ParameterCondition

from kemper import KemperActionDefinitions, KemperEffectSlot, KemperMappings, KemperMidiValueProvider
from display import DISPLAY_ID_FOOTER, DISPLAY_ID_HEADER


# Layout used for the action labels (only used here locally)
_ACTION_LABEL_LAYOUT = {
    "font": "/fonts/H20.pcf",
    "backColor": DEFAULT_LABEL_COLOR,
    "stroke": 1
}

# Defines the switch assignments
Switches = [

    # Switch 1
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_1,
        "actions": [
            KemperActionDefinitions.TUNER_MODE(
                display = {
                    "id": DISPLAY_ID_HEADER,
                    "index": 0,
                    "layout": _ACTION_LABEL_LAYOUT
                }
            )
        ]
    },

    # Switch 2
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_2,
        "actions": [
            HoldAction({
                "actions": [
                    # Tap tempo incl. blinking
                    KemperActionDefinitions.TAP_TEMPO(),
                    KemperActionDefinitions.SHOW_TEMPO(),
                    KemperActionDefinitions.START_CLOCK()
                ],
                "actionsHold": [
                    # Freeze
                    ParameterAction({
                        "mapping": KemperMappings.FREEZE(KemperEffectSlot.EFFECT_SLOT_ID_DLY),
                        "display": {
                            "id": DISPLAY_ID_HEADER,
                            "index": 1,
                            "layout": _ACTION_LABEL_LAYOUT                            
                        },
                        "text": "Freeze",
                        "color": Colors.DARK_GREEN,
                        "mode": PushButtonAction.LATCH
                    }),

                    # Set delay mix to 1:1 when enabled, remembering the olf setting
                    ParameterAction({
                        "mode": PushButtonAction.LATCH,
                        "mapping": KemperMappings.EFFECT_MIX(
                            slot_id = KemperEffectSlot.EFFECT_SLOT_ID_DLY
                        ),
                        "valueEnable": KemperMidiValueProvider.NRPN_VALUE(0.5),
                        "valueDisable": "auto",
                        "useSwitchLeds": False
                    })
                ]
            })
        ]
    },

    # Switch A
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_A,
        "actions": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A,
                display = {
                    "id": DISPLAY_ID_FOOTER,
                    "index": 0,
                    "layout": _ACTION_LABEL_LAYOUT
                }
            )
        ]
    },
    
    # Switch B
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_B,
        "actions": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_B,
                display = {
                    "id": DISPLAY_ID_FOOTER,
                    "index": 1,
                    "layout": _ACTION_LABEL_LAYOUT
                }
            )
        ]
    },
]
