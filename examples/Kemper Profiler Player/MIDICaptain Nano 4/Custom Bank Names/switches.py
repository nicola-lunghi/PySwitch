##############################################################################################################################################
# 
# Definition of actions for switches
#
##############################################################################################################################################
 
from pyswitch.hardware.Hardware import Hardware

from pyswitch.misc import Colors
from pyswitch.controller.actions.actions import HoldAction

from pyswitch.clients.kemper import KemperActionDefinitions, KemperEffectSlot, KemperMappings, RIG_SELECT_DISPLAY_TARGET_RIG, RIG_SELECT_DISPLAY_CURRENT_RIG
from display import DISPLAY_HEADER_1, DISPLAY_HEADER_2, DISPLAY_FOOTER_1, DISPLAY_FOOTER_2

# Custom callback to get label text. Bank and rig come with values starting at zero (rig is in range [0..4] and bank in range [0..x] depending on your player level)
def get_custom_text(bank, rig):
    if bank == 0:
        return "Homer " + repr(rig + 1)
    elif bank == 1:
        return "Marge " + repr(rig + 1)
    elif bank == 2:
        return "Bart " + repr(rig + 1)
    elif bank == 3:
        return "Lisa " + repr(rig + 1)
    elif bank == 4:
        return "Maggie " + repr(rig + 1)
    else:
        # Standard behaviour for all other banks
        return "Rig " + repr(bank + 1) + "-" + repr(rig + 1)

# Defines the switch assignments
Switches = [

    # Switch 1
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_1,
        "actions": [
            KemperActionDefinitions.RIG_SELECT(
                rig = 1,                
                display = DISPLAY_HEADER_1,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                text_callback = get_custom_text
            )
        ]
    },

    # Switch 2
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_2,
        "actions": [
            KemperActionDefinitions.RIG_AND_BANK_SELECT(
                rig = 2,               
                bank = 3,
                display = DISPLAY_HEADER_2,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                text_callback = get_custom_text
            )
        ]
    },

    # Switch A
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_A,
        "actions": [
            KemperActionDefinitions.RIG_SELECT(
                rig = 1,
                rig_off = 2,                
                display = DISPLAY_FOOTER_1,
                display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG,
                text_callback = get_custom_text
            )
        ]
    },
    
    # Switch B
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_B,
        "actions": [
            KemperActionDefinitions.BANK_UP(
                display = DISPLAY_FOOTER_2,
                text_callback = get_custom_text,
                display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG,
            )            
        ]
    }
]
