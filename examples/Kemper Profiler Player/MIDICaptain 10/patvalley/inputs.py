##############################################################################################################################################
# 
# Definition of actions for switches
#
##############################################################################################################################################
 
from pyswitch.hardware.devices.pa_midicaptain_10 import *

from pyswitch.clients.kemper import KemperEffectSlot
from pyswitch.controller.actions import PushButtonAction
from display import DISPLAY_FOOTER_1, DISPLAY_FOOTER_2, DISPLAY_HEADER_1, DISPLAY_HEADER_2

from pyswitch.clients.kemper.actions.effect_state import KemperEffectEnableCallback
from pyswitch.clients.kemper.actions.bank_up_down import BANK_UP, BANK_DOWN
from pyswitch.clients.kemper.actions.rig_select import RIG_SELECT, RIG_SELECT_DISPLAY_CURRENT_RIG

#####################################################################################################

# Current Bank/Rig display: Define a custom text callback for all RIG_SELECTs, to get rid of the "Rig " prefix of the original.
def _text_callback(action, bank, rig):
    return f"{bank + 1} - {rig + 1}"

#####################################################################################################

# Category names: Instead of using EFFECT_STATE, you can define the PushButtonAction manually, overriding the
# callback to deliver different effect category names: First override the respective method:
class MyKemperEffectEnableCallback(KemperEffectEnableCallback):
    # Just redefine the names method (this implementation will override the original one)
    def get_effect_category_text(self, category):
        if category == self.CATEGORY_CHORUS:
            return "Mod Ch/Tr"
        elif category == self.CATEGORY_PHASER_FLANGER:
            return "Mod Ph/Fl"
        else:
            # Fall back to the original implementation for all others
            return super().get_effect_category_text(category)

# Now define our custom action, which is used instead of EFFECT_STATE
def MY_EFFECT_STATE(slot_id, display = None):
    return PushButtonAction({
        "callback": MyKemperEffectEnableCallback(slot_id),  # Use our own callback here!
        "mode": PushButtonAction.HOLD_MOMENTARY,
        "display": display,
        "useSwitchLeds": True
    })

#####################################################################################################

# Defines the switch assignments
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
        ]
    },


    # Switch A
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_A,
        "actions": [
            RIG_SELECT(
                rig = 1,
                display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG,  # Use CURRENT instead of TARGET makes the RIG_SELECT action show the current 
                                                                # bank/rig ind bank color. This makes no difference to the LEDs as the target bank
                                                                # always is the current bank.

                display = DISPLAY_FOOTER_2,                     # This action will control FOOTER_2
                text_callback = _text_callback                  # Pass our own text formatter function
            )
        ]
    },


    # Switch B
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_B,
        "actions": [
            RIG_SELECT(
                rig = 2
            )
        ]
    },


    # Switch C
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_C,
        "actions": [
            RIG_SELECT(
                rig = 3
            )
        ]
    },


    # Switch D
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_D,
        "actions": [
            RIG_SELECT(
                rig = 4
            )
        ]
    },


    # Switch down
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_DOWN,
        "actions": [
            RIG_SELECT(
                rig = 5
	    )
        ]
    }
]
