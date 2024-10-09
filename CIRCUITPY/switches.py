##############################################################################################################################################
# 
# Definition of actions for switches
#
##############################################################################################################################################
 
from pyswitch.hardware.hardware import SwitchDefinitions

from pyswitch.misc import Colors, Defaults
from pyswitch.controller.ConditionTree import ParameterCondition, ParameterConditionModes
from pyswitch.controller.actions.actions import PushButtonModes

from kemper import Kemper, KemperActionDefinitions, KemperEffectSlot, KemperMappings, KemperMidiValueProvider
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

# Defines the switch assignments
Switches = [

    # Switch 1
    {
        "assignment": SwitchDefinitions.PA_MIDICAPTAIN_NANO_SWITCH_1,
        "actions": [
            #KemperActionDefinitions.EFFECT_ON_OFF(
            #    slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A,
            #    display = {
            #        "id": DisplayIds.DISPLAY_HEADER,
            #        "index": 0,
            #        "layout": ACTION_LABEL_LAYOUT
            #    }
            #)
            ParameterCondition(
                mapping = KemperMappings.RIG_VOLUME,
                mode = ParameterConditionModes.MODE_GREATER_EQUAL,
                ref_value = Kemper.NRPN_VALUE(0.5),

                yes = [
                    KemperActionDefinitions.EFFECT_ON_OFF(
                        id = "sw1",
                        slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A,
                    ),
                    KemperActionDefinitions.EFFECT_ON_OFF(
                        slot_id = KemperEffectSlot.EFFECT_SLOT_ID_REV,
                        display = {
                            "id": DisplayIds.DISPLAY_HEADER,
                            "index": 0,
                            "layout": ACTION_LABEL_LAYOUT
                        }
                    ),
                    KemperActionDefinitions.AMP_ON_OFF()
                ],
                no = KemperActionDefinitions.EFFECT_ON_OFF(
                    slot_id = KemperEffectSlot.EFFECT_SLOT_ID_DLY,
                    display = {
                        "id": DisplayIds.DISPLAY_HEADER,
                        "index": 0,
                        "layout": ACTION_LABEL_LAYOUT
                    }
                )
            )                
        ]
    },

    # Switch 2
    {
        "assignment": SwitchDefinitions.PA_MIDICAPTAIN_NANO_SWITCH_2,
        "actions": [
            KemperActionDefinitions.EFFECT_ON_OFF(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_B,
                display = {
                    "id": DisplayIds.DISPLAY_HEADER,
                    "index": 1,
                    "layout": ACTION_LABEL_LAYOUT
                },
                mode = PushButtonModes.MOMENTARY
            )
        ]
    },

    # Switch A
    {
        "assignment": SwitchDefinitions.PA_MIDICAPTAIN_NANO_SWITCH_A,
        "actions": [
            KemperActionDefinitions.AMP_ON_OFF(
                display = {
                    "id": DisplayIds.DISPLAY_FOOTER,
                    "index": 0,
                    "layout": ACTION_LABEL_LAYOUT
                },
                color = (Colors.WHITE, Colors.YELLOW, Colors.LIGHT_GREEN)  
            )
        ]
    },
    
    # Switch B
    {
        "assignment": SwitchDefinitions.PA_MIDICAPTAIN_NANO_SWITCH_B,
        "actions": [
            KemperActionDefinitions.RESET_RIG_INFO_DISPLAYS(),
            KemperActionDefinitions.RIG_SELECT(
                rig = 1,
                bank = 1,

                rig_off = 5,
                bank_off = 3,

                display = {
                    "id": DisplayIds.DISPLAY_FOOTER,
                    "index": 1,
                    "layout": ACTION_LABEL_LAYOUT
                }   
            )
        ]
    }
]
