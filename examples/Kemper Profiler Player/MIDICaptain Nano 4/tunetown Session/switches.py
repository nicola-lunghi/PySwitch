##############################################################################################################################################
# 
# Definition of actions for switches
#
##############################################################################################################################################
 
from pyswitch.hardware.Hardware import Hardware

from pyswitch.misc import Colors

from pyswitch.clients.kemper import KemperActionDefinitions, KemperEffectSlot, KemperMappings, RIG_SELECT_DISPLAY_TARGET_RIG
from display import DISPLAY_HEADER_1, DISPLAY_HEADER_2, DISPLAY_FOOTER_1, DISPLAY_FOOTER_2

##############################################################################################################################################

# Defines the switch assignments
Switches = [

    # Switch 1
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_1,
        "actions": [
            KemperActionDefinitions.TAP_TEMPO(use_leds = False),
            KemperActionDefinitions.SHOW_TEMPO(    # Shows beats with the LED(s)
                led_brightness_on = 0.02,
                led_brightness_off = 0
            )
        ],
        "actionsHold": [
            KemperActionDefinitions.TUNER_MODE(
                display = DISPLAY_HEADER_1,
                text = "Tap|Tune"
            )            
        ]
    },

    # Switch 2
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_2,
        "actions": [
            # Freeze on/off
            KemperActionDefinitions.BINARY_SWITCH(
                mapping = KemperMappings.FREEZE(KemperEffectSlot.EFFECT_SLOT_ID_DLY),
                display = DISPLAY_HEADER_2,
                text = "Freeze",
                color = Colors.LIGHT_GREEN
            )
        ]
    },

    # Switch A
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_A,
        "actions": [
            KemperActionDefinitions.RIG_SELECT(
                rig = 4,
                rig_off = "auto",
                auto_exclude_rigs = (4, 5),
                display = DISPLAY_FOOTER_1,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                color = Colors.PINK,
                text = "Synth-4"
            )   
        ]
    },
    
    # Switch B
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_B,
        "actions": [
            KemperActionDefinitions.RIG_SELECT(
                rig = 5,
                rig_off = "auto",
                auto_exclude_rigs = (4, 5),
                display = DISPLAY_FOOTER_2,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                color = Colors.RED,
                text = "Lead-5"
            )
        ]
    },
]
