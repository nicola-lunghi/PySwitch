##############################################################################################################################################
# 
# Definition of actions for switches
#
##############################################################################################################################################
 
from pyswitch.hardware.Hardware import Hardware

#from pyswitch.misc import Colors

from pyswitch.clients.kemper import KemperActionDefinitions, KemperEffectSlot #, KemperMappings
from display import DISPLAY_HEADER_1, DISPLAY_HEADER_2, DISPLAY_FOOTER_1, DISPLAY_FOOTER_2


# Defines the switch assignments
Switches = [

    # Switch 1
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_1,
        "actions": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A,
                display = DISPLAY_HEADER_1
            )                         
        ]
    },

    # Switch 2
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_2,
        "actions": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_B,
                display = DISPLAY_HEADER_2
            )
        ]
    },

    # Switch 3
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_3,
        "actions": [
            KemperActionDefinitions.TUNER_MODE()
        ]
    },

    # Switch A
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_A,
        "actions": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_DLY,
                display = DISPLAY_FOOTER_1
            )        
        ]
    },
    
    # Switch B
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_B,
        "actions": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_REV,
                display = DISPLAY_FOOTER_2
            )        
        ]
    },

    # Switch C
    {
        "assignment": Hardware.PA_MIDICAPTAIN_MINI_SWITCH_C,
        "actions": [
            KemperActionDefinitions.RIG_VOLUME_BOOST(
                boost_volume = 0.625  # +3dB          # Value im [0..1] representing the Rig Volume Knob. Examples: 0.5 = 0dB (no boost), 0.75 = +6dB, 1.0 = +12dB
            )        
        ]
    }
]
