##############################################################################################################################################
# 
# Definition of actions for switches
#
##############################################################################################################################################
 
from pyswitch.hardware.Hardware import Hardware

from pyswitch.misc import DEFAULT_LABEL_COLOR, Colors
from pyswitch.controller.actions.actions import HoldAction, ParameterAction, PushButtonAction
#from pyswitch.controller.ConditionTree import ParameterCondition

from kemper import KemperActionDefinitions, KemperEffectSlot, KemperMappings, KemperMidiValueProvider, CC_MORPH_PEDAL, ClientParameterMapping
from adafruit_midi.control_change import ControlChange
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
                    # Tap tempo / Tempo display
                    KemperActionDefinitions.TAP_TEMPO(use_leds = False),
                    KemperActionDefinitions.SHOW_TEMPO()    # Shows beats with the LED(s)
                ],
                "actionsHold": [
                    # Enable delay (also on disable!)
                    ParameterAction({
                        "mode": PushButtonAction.ENABLE,
                        "mapping": KemperMappings.EFFECT_STATE(
                            slot_id = KemperEffectSlot.EFFECT_SLOT_ID_DLY
                        ),
                        "useSwitchLeds": False
                    }),

                    # Freeze on/off
                    ParameterAction({
                        "mapping": KemperMappings.FREEZE(KemperEffectSlot.EFFECT_SLOT_ID_DLY),
                        "display": {
                            "id": DISPLAY_ID_HEADER,
                            "index": 1,
                            "layout": _ACTION_LABEL_LAYOUT                            
                        },
                        "text": "Tap|Frz",
                        "color": Colors.GREEN,
                        "mode": PushButtonAction.LATCH
                    }),                    

                    # Set delay mix to 1:1 when enabled, remembering the old setting
                    ParameterAction({
                        "mode": PushButtonAction.LATCH,
                        "mapping": KemperMappings.EFFECT_MIX(
                            slot_id = KemperEffectSlot.EFFECT_SLOT_ID_DLY
                        ),
                        "valueEnable": KemperMidiValueProvider.NRPN_VALUE(0.5),
                        "valueDisable": "auto",
                        "comparisonMode": ParameterAction.EQUAL,
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
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_B,
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
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_C,
                display = {
                    "id": DISPLAY_ID_FOOTER,
                    "index": 1,
                    "layout": _ACTION_LABEL_LAYOUT
                }
            )
        ]
    },
]
