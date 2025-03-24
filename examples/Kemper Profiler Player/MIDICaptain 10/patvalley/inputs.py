from pyswitch.hardware.devices.pa_midicaptain_10 import *
from pyswitch.clients.kemper import KemperEffectSlot
from pyswitch.controller.actions import PushButtonAction
from display import DISPLAY_FOOTER_1, DISPLAY_FOOTER_2, DISPLAY_HEADER_1, DISPLAY_HEADER_2
from pyswitch.clients.kemper.actions.effect_state import KemperEffectEnableCallback
from pyswitch.clients.kemper.actions.bank_up_down import BANK_UP, BANK_DOWN
from pyswitch.clients.kemper.actions.rig_select import RIG_SELECT, RIG_SELECT_DISPLAY_CURRENT_RIG, RIG_SELECT_DISPLAY_TARGET_RIG
from pyswitch.clients.kemper.actions.tuner import TUNER_MODE

# Current Bank/Rig display: Define a custom text callback for all RIG_SELECTs, to get rid of the "Rig " prefix of the original.
def _text_callback(action, bank, rig):
    return f"{bank + 1} - {rig + 1}"

# Category names: Instead of using EFFECT_STATE, you can define the PushButtonAction manually, overriding the
# callback to deliver different effect category names: First override the respective method:
class MyKemperEffectEnableCallback(KemperEffectEnableCallback):
    def get_effect_category_text(self, category, kpp_type):
        if category == self.CATEGORY_CHORUS:
            return "Mod Ch/Tr"
        elif category == self.CATEGORY_PHASER_FLANGER:
            return "Mod Ph/Fl"
        else:
            # Fall back to the original implementation for all others
            return super().get_effect_category_text(category, kpp_type)

# Now define our custom action, which is used instead of EFFECT_STATE
def MY_EFFECT_STATE(slot_id, display = None):
    return PushButtonAction({
        "callback": MyKemperEffectEnableCallback(slot_id),
        "mode": PushButtonAction.HOLD_MOMENTARY,
        "display": display,
        "useSwitchLeds": True
    })


Inputs = [
    # Switch 1
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_1,
        "actions": [
            MY_EFFECT_STATE(                                              # Use our own effect state action
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_C,
                display = DISPLAY_HEADER_1
            )                       
        ]
    },


    # Switch 2
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_2,
        "actions": [
            MY_EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_X,
                display = DISPLAY_HEADER_2
            )
        ]
    },


    # Switch 3
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_3,
        "actions": [
            MY_EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_MOD,
                display = DISPLAY_FOOTER_1
            )
        ]
    },
    
    # Switch 4
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_4,
        "actions": [
            BANK_DOWN()
        ]
    },


    # Switch up
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_UP,
        "actions": [
            BANK_UP()
        ],
        "actionsHold": [
            TUNER_MODE()
        ],
        #"holdTimeMillis": 9999999   # Uncomment this to disable the tuner action (you have to hold for veeery long to activate it)
    },

    #####################################################################

    # Switch A
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_A,
        "actions": [
            RIG_SELECT(
                rig = 1,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
            )
        ],

        # This action is disabled by setting the hold time to a very high value, and just serves as "driver" for DISPLAY_FOOTER_2
        "actionsHold": [
            RIG_SELECT(
                rig = 1,
                display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG,   # Use CURRENT instead of TARGET makes the RIG_SELECT action show the current 
                                                                 # bank/rig ind bank color. This makes no difference to the LEDs as the target bank
                                                                 # always is the current bank.

                display = DISPLAY_FOOTER_2,                      # This action will control FOOTER_2
                text_callback = _text_callback                   # Pass our own text formatter function
            )
        ],
        "holdTimeMillis": 9999999
    },


    # Switch B
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_B,
        "actions": [
            RIG_SELECT(
                rig = 2,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
            )
        ]
    },


    # Switch C
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_C,
        "actions": [
            RIG_SELECT(
                rig = 3,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
            )
        ]
    },


    # Switch D
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_D,
        "actions": [
            RIG_SELECT(
                rig = 4,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
            )
        ]
    },


    # Switch down
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_DOWN,
        "actions": [
            RIG_SELECT(
                rig = 5,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
	    )
        ]
    }
]
