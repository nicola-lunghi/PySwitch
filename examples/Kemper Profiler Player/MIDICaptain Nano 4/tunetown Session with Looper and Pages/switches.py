##############################################################################################################################################
# 
# Definition of actions for switches
#
##############################################################################################################################################
 
from pyswitch.hardware.Hardware import Hardware

from pyswitch.misc import Colors

from pyswitch.clients.kemper import KemperMappings, RIG_SELECT_DISPLAY_TARGET_RIG
from pyswitch.controller.callbacks import Callback
from pyswitch.controller.actions import PushButtonAction
from display import DISPLAY_HEADER_1, DISPLAY_HEADER_2, DISPLAY_FOOTER_1, DISPLAY_FOOTER_2

from pyswitch.clients.kemper.actions.tempo import TAP_TEMPO, SHOW_TEMPO
from pyswitch.clients.kemper.actions.tuner import TUNER_MODE
from pyswitch.clients.kemper.actions.binary_switch import BINARY_SWITCH
from pyswitch.clients.kemper.actions.rig_select import RIG_SELECT

##############################################################################################################################################

# Define some page IDs
_PAGE_1 = 10
_PAGE_2 = 20

# Paging controller. The Pager Callback acts both as action and enable callback for other actions.
_pager = PageFlipCallback(
    pages = [
        _PAGE_1,
        _PAGE_2
    ]
)

##############################################################################################################################################

# Defines the switch assignments
Switches = [

    # Switch 1
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_1,
        "actions": [
            TAP_TEMPO(use_leds = False),
            SHOW_TEMPO()    # Shows beats with the LED(s)
        ],
        "actionsHold": [
            TUNER_MODE(
                display = DISPLAY_HEADER_1,
                text = "Tap|Tune"
            )            
        ]
    },

    # Switch 2
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_2,
        "actions": [
            # Looper Rec/Play/Overdub
            BINARY_SWITCH(
                mapping = KemperMappings.LOOPER_REC_PLAY_OVERDUB(),
                color = Colors.LIGHT_GREEN,
                mode = PushButtonAction.MOMENTARY,
                display = DISPLAY_HEADER_2,
                text = "Rec"
            )
        ],
        "actionsHold": [
            # Looper Erase
            BINARY_SWITCH(
                mapping = KemperMappings.LOOPER_ERASE(),
                color = Colors.RED,
                mode = PushButtonAction.MOMENTARY
            )
        ]
    },

    #############################################################################

    # Switch A
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_A,
        "actions": [
            # Page 1: Rig select
            RIG_SELECT(
                rig = 4,
                rig_off = "auto",
                auto_exclude_rigs = (4, 5),
                display = DISPLAY_FOOTER_1,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                color = Colors.PINK,
                text = "Synth-4",
                id = _PAGE_1,
                enable_callback = _pager
            ),
            
            # Page 2: Looper Cancel/Reactivate Overdub
            BINARY_SWITCH(
                mapping = KemperMappings.LOOPER_CANCEL(),
                color = Colors.LIGHT_GREEN,
                mode = PushButtonAction.MOMENTARY,
                display = DISPLAY_FOOTER_1,
                text = "Undo",
                id = _PAGE_2,
                enable_callback = _pager
            )
        ],
        "actionsHold": [
            # Pahe 2: Looper Reverse
            BINARY_SWITCH(
                mapping = KemperMappings.LOOPER_REVERSE(),
                color = Colors.LIGHT_YELLOW,
                mode = PushButtonAction.MOMENTARY,
                id = _PAGE_2,
                enable_callback = _pager
            )
        ]     
    },
    
    # Switch B
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_B,
        "actions": [
            # Page 1: Rig select
            RIG_SELECT(
                rig = 5,
                rig_off = "auto",
                auto_exclude_rigs = (4, 5),
                display = DISPLAY_FOOTER_2,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                color = Colors.RED,
                text = "Lead-5",
                id = _PAGE_1,
                enable_callback = _pager
            ),

            # Page 2: Looper Stop
            BINARY_SWITCH(
                mapping = KemperMappings.LOOPER_STOP(),
                color = Colors.LIGHT_RED,
                mode = PushButtonAction.MOMENTARY,
                display = DISPLAY_FOOTER_2,
                text = "Stop",
                id = _PAGE_2,
                enable_callback = _pager
            )
        ],
        "actionsHold": [
            # Toggle pages. The Pager Callback acts both as action and enable callback for other actions.
            _pager
        ]
    },
]
