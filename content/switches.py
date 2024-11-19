##############################################################################################################################################
# 
# Definition of actions for switches
#
##############################################################################################################################################
 
from pyswitch.hardware.Hardware import Hardware

from pyswitch.misc import Colors, Callback
from pyswitch.controller.actions.actions import HoldAction, ParameterAction, PushButtonAction

from kemper import KemperActionDefinitions, KemperEffectSlot, KemperMappings, NRPN_VALUE
from display import DISPLAY_HEADER_1, DISPLAY_HEADER_2, DISPLAY_FOOTER_1, DISPLAY_FOOTER_2

class _EnableCallback(Callback):
    def __init__(self):
        Callback.__init__(self)
        self.mapping = KemperMappings.RIG_VOLUME()

    def get_mappings(self):
        yield self.mapping

    def get(self, action):  
        if self.mapping.value == None:
            return (action.id == 10)
        
        if action.id == 10:
            return (self.mapping.value >= NRPN_VALUE(0.5))
        if action.id == 20:
            return (self.mapping.value < NRPN_VALUE(0.5))
        
_enable_callback = _EnableCallback()


# Defines the switch assignments
Switches = [

    # Switch 1
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_1,
        "actions": [
            KemperActionDefinitions.TUNER_MODE(
                id = 10,
                display = DISPLAY_HEADER_1,
                enable_callback = _enable_callback
            ),

            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_B,
                id = 20,
                display = DISPLAY_HEADER_1,
                enable_callback = _enable_callback
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
                        "display": DISPLAY_HEADER_2,
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
                        "valueEnable": NRPN_VALUE(0.5),
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
                display = DISPLAY_FOOTER_1
            )
        ]
    },
    
    # Switch B
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_B,
        "actions": [
            KemperActionDefinitions.RIG_SELECT(
                #slot_id = KemperEffectSlot.EFFECT_SLOT_ID_C,
                rig = 1,
                bank = 2,
                rig_off = 3,
                bank_off = 3,
                display = DISPLAY_FOOTER_2
            )
        ]
    },
]
