##############################################################################################################################################
# 
# Definition of actions for switches
#
##############################################################################################################################################
 
from pyswitch.hardware.hardware import SwitchDefinitions

from pyswitch.misc import Colors, Defaults
from pyswitch.controller.ConditionTree import ParameterCondition, ParameterConditionModes
from pyswitch.controller.actions.actions import PushButtonModes, ParameterAction

from kemper import KemperActionDefinitions, KemperEffectSlot, KemperMappings, KemperMidiValueProvider
from displays import DisplayIds


# Layout used for the action labels (only used here locally)
ACTION_LABEL_LAYOUT = {
    "font": "/fonts/H20.pcf",
    "backColor": Defaults.DEFAULT_LABEL_COLOR,
    "stroke": 1
}

# Value provider which is responsible for setting values on MIDI messages for value changes, and parse MIDI messages
# when an answer to a value request is received.
ValueProvider = KemperMidiValueProvider()

# Predefine display addressing (will be the same for all condition branches). 
# See below for explanation on action displays.
SW1_DISPLAY = {
	"id": DisplayIds.DISPLAY_HEADER, 
	"index": 0,
	"layout": ACTION_LABEL_LAYOUT
}

# Defines the switch assignments
Switches = [

    # Switch 1
    {
        "assignment": SwitchDefinitions.PA_MIDICAPTAIN_MINI_SWITCH_1,
        "actions": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A,
                display = {
                    "id": DisplayIds.DISPLAY_HEADER,
                    "index": 0,
                    "layout": ACTION_LABEL_LAYOUT
                }
            )                         
        ]
    },

    # Switch 2
    {
        "assignment": SwitchDefinitions.PA_MIDICAPTAIN_MINI_SWITCH_2,
        "actions": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_B,
                display = {
                    "id": DisplayIds.DISPLAY_HEADER,
                    "index": 1,
                    "layout": ACTION_LABEL_LAYOUT
                }
            )
        ]
    },

    # Switch 3
    {
        "assignment": SwitchDefinitions.PA_MIDICAPTAIN_MINI_SWITCH_3,
        "actions": [
            KemperActionDefinitions.TUNER_MODE(
                display = {
                    "id": DisplayIds.DISPLAY_TUNER
                }                
            )
        ]
    },

    # Switch A
    {
        "assignment": SwitchDefinitions.PA_MIDICAPTAIN_MINI_SWITCH_A,
        "actions": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_DLY,
                display = {
                    "id": DisplayIds.DISPLAY_FOOTER,
                    "index": 0,
                    "layout": ACTION_LABEL_LAYOUT
                }
            )        
        ]
    },
    
    # Switch B
    {
        "assignment": SwitchDefinitions.PA_MIDICAPTAIN_MINI_SWITCH_B,
        "actions": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_REV,
                display = {
                    "id": DisplayIds.DISPLAY_FOOTER,
                    "index": 1,
                    "layout": ACTION_LABEL_LAYOUT
                }
            )        
        ]
    },

    # Switch C
    {
        "assignment": SwitchDefinitions.PA_MIDICAPTAIN_MINI_SWITCH_C,
        "actions": [
            KemperActionDefinitions.RIG_VOLUME_BOOST(
                boost_volume = 0.75,    # Value im [0..1] representing the Rig Volume Knob. Examples: 0.5 = 0dB (no boost), 0.75 = +6dB, 1.0 = +12dB
                display = {
                    "id": DisplayIds.DISPLAY_BOOST
                }
            )        
        ]
    }
]
