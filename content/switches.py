##############################################################################################################################################
# 
# Definition of actions for switchessd
#
##############################################################################################################################################
 
from pyswitch.hardware.Hardware import Hardware

from pyswitch.misc import Colors
from pyswitch.controller.actions.actions import HoldAction, PushButtonAction
from pyswitch.controller.callbacks import BinaryParameterCallback

from pyswitch.clients.kemper import KemperActionDefinitions, KemperEffectSlot, KemperMappings, NRPN_VALUE
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
            HoldAction({
                "actions": [
                    # Tap tempo / Tempo display
                    KemperActionDefinitions.TAP_TEMPO(use_leds = False),
                    KemperActionDefinitions.SHOW_TEMPO()    # Shows beats with the LED(s)
                ],
                "actionsHold": [
                    # Enable delay (also on disable!)
                    PushButtonAction({
                        "callback": BinaryParameterCallback(
                            mapping = KemperMappings.EFFECT_STATE(slot_id = KemperEffectSlot.EFFECT_SLOT_ID_DLY)                            
                        ),
                        "mode": PushButtonAction.ENABLE
                    }),

                    # Freeze on/off
                    PushButtonAction({
                        "callback": BinaryParameterCallback(
                            mapping = KemperMappings.FREEZE(KemperEffectSlot.EFFECT_SLOT_ID_DLY),
                            text = "Tap|Frz",
                            color = Colors.GREEN
                        ),
                        "mode": PushButtonAction.LATCH,
                        "display": DISPLAY_HEADER_2,
                        "useSwitchLeds": True
                    }),                    

                    # Set delay mix to a fix value when enabled, remembering the old setting
                    #PushButtonAction({
                    #    "callback": BinaryParameterCallback(
                    #        mapping = KemperMappings.DELAY_MIX(slot_id = KemperEffectSlot.EFFECT_SLOT_ID_DLY),
                    #        value_enable = NRPN_VALUE(0.5),  # 100%
                    #        value_disable = "auto",
                    #        comparison_mode = BinaryParameterCallback.EQUAL,
                    #    ),
                    #    "mode": PushButtonAction.LATCH
                    #})
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
                display = DISPLAY_FOOTER_1
            )
        ]
    },
    
    # Switch B
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_B,
        "actions": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_C,
                display = DISPLAY_FOOTER_2
            )
        ]
    },
]
