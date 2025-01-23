##############################################################################################################################################
# 
# Definition of actions for switches
#
##############################################################################################################################################
 
from pyswitch.hardware.devices.pa_midicaptain_nano_4 import *

from pyswitch.misc import Colors

from pyswitch.controller.pager import PagerAction
from display import DISPLAY_HEADER_1, DISPLAY_HEADER_2, DISPLAY_FOOTER_1, DISPLAY_FOOTER_2, DISPLAY_PAGE

from pyswitch.clients.kemper.actions.tempo import TAP_TEMPO, SHOW_TEMPO
from pyswitch.clients.kemper.actions.tuner import TUNER_MODE
from pyswitch.clients.kemper.actions.rig_select import RIG_SELECT, RIG_SELECT_DISPLAY_TARGET_RIG

from pyswitch.clients.kemper.actions.looper import LOOPER_REC_PLAY_OVERDUB, LOOPER_STOP, LOOPER_ERASE, LOOPER_CANCEL, LOOPER_REVERSE

##############################################################################################################################################

# Define some page IDs
_PAGE_1 = 10
_PAGE_2 = 20

# Paging controller. 
_pager = PagerAction(
    pages = [
        {
            "id": _PAGE_1, 
            "color": Colors.BLACK,
            "text": "                                                              Looper"  # Cheap trick to get this aligned right....
        },
        {
            "id": _PAGE_2, 
            "color": Colors.LIGHT_GREEN,
            "text": "L  O  O  P  E  R"
        },
    ],
    config = {
        "display": DISPLAY_PAGE
    }
)

##############################################################################################################################################

# Defines the switch assignments
Inputs = [

    # Switch 1
    {
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_1,
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
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_2,
        "actions": [
            # Page 1: Looper Rec/Play/Overdub
            LOOPER_REC_PLAY_OVERDUB(
                color = Colors.LIGHT_GREEN,
                display = DISPLAY_HEADER_2,
                text = "Rec|Erase",
                id = _PAGE_1,
                enable_callback = _pager.enable_callback
            ),

            # Page 2: Looper Stop
            LOOPER_STOP(
                color = Colors.LIGHT_RED,
                display = DISPLAY_HEADER_2,
                text = "Stp|Erase",
                id = _PAGE_2,
                enable_callback = _pager.enable_callback
            )
        ],
        "actionsHold": [
            # Page 1: Looper Erase
            LOOPER_ERASE(
                color = Colors.RED
            )
        ]
    },

    #############################################################################

    # Switch A
    {
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_A,
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
                enable_callback = _pager.enable_callback
            ),
            
            # Page 2: Looper Cancel/Reactivate Overdub
            LOOPER_CANCEL(
                color = Colors.LIGHT_GREEN,
                display = DISPLAY_FOOTER_1,
                text = "Undo|Rev",
                id = _PAGE_2,
                enable_callback = _pager.enable_callback
            )
        ],
        "actionsHold": [
            # Pahe 2: Looper Reverse
            LOOPER_REVERSE(
                color = Colors.YELLOW,
                id = _PAGE_2,
                enable_callback = _pager.enable_callback
            )
        ]     
    },
    
    # Switch B
    {
        "assignment": PA_MIDICAPTAIN_NANO_SWITCH_B,
        "actions": [
            # Page 1: Rig select
            RIG_SELECT(
                rig = 5,
                rig_off = "auto",
                auto_exclude_rigs = (4, 5),
                display = DISPLAY_FOOTER_2,
                display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
                color = Colors.RED,
                text = "Lead-5|Lp",
                id = _PAGE_1,
                enable_callback = _pager.enable_callback
            ),

            # Page 1: Looper Rec/Play/Overdub
            LOOPER_REC_PLAY_OVERDUB(
                color = Colors.LIGHT_GREEN,
                display = DISPLAY_FOOTER_2,
                text = "Rec|Exit",
                id = _PAGE_2,
                enable_callback = _pager.enable_callback
            ),
        ],
        "actionsHold": [
            # Toggle pages. The Pager Callback acts both as action and enable callback for other actions.
            _pager
        ]
    },
]
