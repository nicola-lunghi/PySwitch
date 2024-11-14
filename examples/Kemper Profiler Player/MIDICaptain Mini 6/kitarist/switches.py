##############################################################################################################################################
# 
# Definition of actions for switches
#
##############################################################################################################################################
 
from pyswitch.hardware.Hardware import Hardware

from pyswitch.misc import Colors, DEFAULT_LABEL_COLOR
from pyswitch.controller.ConditionTree import ParameterCondition
from pyswitch.controller.actions.actions import PushButtonAction, ParameterAction, HoldAction

from kemper import KemperActionDefinitions, KemperEffectSlot, KemperMappings
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
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_1,
        "actions": HoldAction({
            "actions": KemperActionDefinitions.RIG_SELECT(
                rig = 1,
                color = Colors.YELLOW
            ),
            "actionsHold": KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_C,
                display = {
                    "id": DISPLAY_ID_HEADER,
                    "index": 0,
                    "layout": _ACTION_LABEL_LAYOUT
                }
            )       
        }) 
    },

    # Switch 2
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_2,
        "actions": HoldAction({
            "actions": KemperActionDefinitions.RIG_SELECT(
                rig = 2,
                color = Colors.YELLOW
            ),
            "actionsHold": KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_D,
                display = {
                    "id": DISPLAY_ID_HEADER,
                    "index": 1,
                    "layout": _ACTION_LABEL_LAYOUT
                }
            )       
        }) 
    },

    # Switch 3
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_3,
        "actions": HoldAction({
            "actions": KemperActionDefinitions.RIG_SELECT(
                rig = 3,
                color = Colors.YELLOW
            ),
            "actionsHold": KemperActionDefinitions.TUNER_MODE()
        }) 
    },

    # Switch A
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_A,
        "actions": HoldAction({
            "actions": KemperActionDefinitions.RIG_SELECT(
                rig = 4,
                color = Colors.YELLOW
            ),
            "actionsHold": KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_MOD,
                display = {
                    "id": DISPLAY_ID_FOOTER,
                    "index": 0,
                    "layout": _ACTION_LABEL_LAYOUT
                }
            )       
        }) 
    },
    
    # Switch B
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_B,
        "actions": HoldAction({
            "actions": KemperActionDefinitions.RIG_SELECT(
                rig = 5,
                color = Colors.YELLOW
            ),
            "actionsHold": KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_DLY,
                display = {
                    "id": DISPLAY_ID_FOOTER,
                    "index": 1,
                    "layout": _ACTION_LABEL_LAYOUT
                }
            )       
        }) 
    },

    # Switch C
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_C,
        "actions": [
            KemperActionDefinitions.TAP_TEMPO(use_leds = False),
            KemperActionDefinitions.SHOW_TEMPO()    # Shows beats with the LED(s)
        ]
    }
]
