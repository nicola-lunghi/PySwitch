##############################################################################################################################################
# 
# Definition of actions for switches DB Version
#
##############################################################################################################################################
 
# AREK777

from pyswitch.hardware.devices.pa_midicaptain_10 import *

# from display import DISPLAY_FOOTER_1, DISPLAY_FOOTER_2, DISPLAY_HEADER_1, DISPLAY_HEADER_2, DISPLAY_HEADER_3

from pyswitch.clients.kemper.actions.bank_select import BANK_SELECT
from pyswitch.clients.kemper.actions.rig_select import RIG_SELECT_DISPLAY_TARGET_RIG
from pyswitch.clients.kemper.actions.rig_select_and_morph_state import RIG_SELECT_AND_MORPH_STATE

from pyswitch.clients.kemper.actions.tuner import TUNER_MODE
from pyswitch.clients.local.actions.binary_switch import BINARY_SWITCH

from pyswitch.clients.kemper.mappings.pedals import MAPPING_VOLUME_PEDAL, MAPPING_WAH_PEDAL
from pyswitch.clients.kemper.mappings.amp import MAPPING_AMP_GAIN, MAPPING_AMP_STATE

from pyswitch.controller.AnalogAction import AnalogAction
from pyswitch.controller.EncoderAction import EncoderAction

# ##################################################################

# Defines the switch assignments and other inputs

Inputs = [
    # Pedal 1
    {
        "assignment": PA_MIDICAPTAIN_10_EXP_PEDAL_1,
        "actions": [
            AnalogAction(
                mapping = MAPPING_VOLUME_PEDAL(),
                auto_calibrate = True
            )
        ]
    },

    # Pedal 2
    {
        "assignment": PA_MIDICAPTAIN_10_EXP_PEDAL_2,
        "actions": [
            AnalogAction(
                mapping = MAPPING_WAH_PEDAL(),
                auto_calibrate = True
            )
        ]
    },

    # Wheel rotary encoder
    {
        "assignment": PA_MIDICAPTAIN_10_WHEEL_ENCODER,
        "actions": [
            EncoderAction(
                mapping = MAPPING_AMP_GAIN()
            )
        ]
    },

    # Wheel push button
    {
        "assignment": PA_MIDICAPTAIN_10_WHEEL_BUTTON,
        "actions": [
            BINARY_SWITCH(
                mapping = MAPPING_AMP_STATE()                
            )
        ]
    },

    ####################################################################################

    # Switch 1
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_1,
        "actions": [
            BANK_SELECT(
                bank = 1,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]    
    },

    # Switch 2
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_2,
        "actions": [
            BANK_SELECT(
                bank = 2,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
            )
        ]    
    },

    # Switch 3
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_3,
        "actions": [
            BANK_SELECT(
                bank = 3,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]    
    },
    
    # Switch 4
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_4,
        "actions": [
            BANK_SELECT(
                bank = 4,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ]
    },

    # Switch up
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_UP,
        "actions": [
            BANK_SELECT(
                bank = 5,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG
            )
        ],
        "actionsHold": [
            TUNER_MODE()
        ]    
    },

    # ########################################################################################

    # Switch A
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_A,
        "actions": [
            RIG_SELECT_AND_MORPH_STATE(
                rig = 1,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                color = (0, 0, 255),   # BLUE
                rig_btn_morph = True
            )    
        ]
    },

    # Switch B
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_B,
        "actions": [
            RIG_SELECT_AND_MORPH_STATE(
                rig = 2,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                color = (255, 255, 0),  # YELLOW
                rig_btn_morph = True
            )
        ]
    },

    # Switch C
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_C,
        "actions": [
            RIG_SELECT_AND_MORPH_STATE(
                rig = 3,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                color = (255, 0, 0),   # RED
                rig_btn_morph = True
            )
        ]
    },

    # Switch D
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_D,
        "actions": [
            RIG_SELECT_AND_MORPH_STATE(
                rig = 4,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                color = (0, 255, 0),   # GREEN
                rig_btn_morph = True
            )
        ]
    },

    # Switch down
    {
        "assignment": PA_MIDICAPTAIN_10_SWITCH_DOWN,
        "actions": [
            RIG_SELECT_AND_MORPH_STATE(
                rig = 5,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                color = (180, 0, 120),   # PURPLE
                rig_btn_morph = True
            )
        ]
    }
]

