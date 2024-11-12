##############################################################################################################################################
# 
# Definition of actions for switches
#
##############################################################################################################################################
 
from pyswitch.hardware.Hardware import Hardware

from pyswitch.misc import DEFAULT_LABEL_COLOR #, Colors
from pyswitch.controller.actions.actions import HoldAction  #, PushButtonAction
#from pyswitch.controller.ConditionTree import ParameterCondition

from kemper import KemperActionDefinitions, KemperEffectSlot #, KemperMappings
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
            HoldAction({
                "actions": [
                    KemperActionDefinitions.EFFECT_STATE(
                        slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A,
                        display = {
                            "id": DISPLAY_ID_HEADER,
                            "index": 0,
                            "layout": _ACTION_LABEL_LAYOUT
                        }
                    )                           
                ],
                "actionsHold": KemperActionDefinitions.BANK_DOWN()
            })
        ]
    },

    # Switch 2
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_2,
        "actions": [
            HoldAction({
                "actions": [
                    KemperActionDefinitions.EFFECT_STATE(
                        slot_id = KemperEffectSlot.EFFECT_SLOT_ID_B,
                        display = {
                            "id": DISPLAY_ID_HEADER,
                            "index": 1,
                            "layout": _ACTION_LABEL_LAYOUT
                        }
                    )                           
                ],
                "actionsHold": KemperActionDefinitions.BANK_UP()
            })
        ]
    },

    # Switch A
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_A,
        "actions": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_DLY,
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
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_REV,
                display = {
                    "id": DISPLAY_ID_FOOTER,
                    "index": 1,
                    "layout": _ACTION_LABEL_LAYOUT
                }
            )
        ]
    },
]
