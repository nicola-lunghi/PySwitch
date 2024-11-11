##############################################################################################################################################
# 
# Definition of actions for switches
#
##############################################################################################################################################
 
from pyswitch.hardware.Hardware import Hardware

from pyswitch.misc import Colors, DEFAULT_LABEL_COLOR
from pyswitch.controller.ConditionTree import ParameterCondition
from pyswitch.controller.actions.actions import ParameterAction, HoldAction

from kemper import KemperActionDefinitions, KemperEffectSlot, KemperMappings
from display import DISPLAY_ID_BOOST, DISPLAY_ID_FOOTER, DISPLAY_ID_HEADER, DISPLAY_ID_TUNER


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
        "actions": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A,
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
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_2,
        "actions": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_B,
                display = {
                    "id": DISPLAY_ID_HEADER,
                    "index": 1,
                    "layout": _ACTION_LABEL_LAYOUT
                }
            )
        ]
    },

    # Switch 3
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_3,
        "actions": [
            KemperActionDefinitions.TUNER_MODE(
                display = {
                    "id": DISPLAY_ID_TUNER
                }                
            )
        ]
    },

    # Switch A
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_A,
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
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_B,
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

    # Switch C
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_C,
        "actions": [
            KemperActionDefinitions.RIG_VOLUME_BOOST(
                boost_volume = 0.75,    # Value im [0..1] representing the Rig Volume Knob. Examples: 0.5 = 0dB (no boost), 0.75 = +6dB, 1.0 = +12dB
                display = {
                    "id": DISPLAY_ID_BOOST
                }
            )        
        ]
    }
]
