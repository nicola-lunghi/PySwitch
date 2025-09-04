from pyswitch.clients.kemper import KemperRigNameCallback
from pyswitch.clients.kemper import TunerDisplayCallback
from micropython import const
from pyswitch.colors import DEFAULT_LABEL_COLOR
from pyswitch.ui.ui import DisplayElement
from pyswitch.ui.ui import DisplayBounds
from pyswitch.ui.elements import DisplayLabel
from pyswitch.ui.elements import BidirectionalProtocolState

_ACTION_LABEL_LAYOUT = {
    "font": "/fonts/H20.pcf",
    "backColor": DEFAULT_LABEL_COLOR,
    "stroke": 1,
    
}

_DISPLAY_WIDTH = const(
    246
)
_DISPLAY_HEIGHT = const(
    240
)
_SLOT_WIDTH = const(
    60
)
_SLOT_HEIGHT = const(
    30
)
_FOOTER_Y = const(
    180
)
_FOOTER_Y2 = const(
    210
)
_RIG_ID_HEIGHT = const(40)
_RIG_NAME_HEIGHT = const(
    120
)
_RIG_ID_Y = const(160)


DISPLAY_HEADER_1 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT, 
    bounds = DisplayBounds(
        x = 0, 
        y = 0, 
        w = _SLOT_WIDTH, 
        h = _SLOT_HEIGHT
    )
)
DISPLAY_HEADER_2 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT, 
    bounds = DisplayBounds(
        x = 60, 
        y = 0, 
        w = _SLOT_WIDTH, 
        h = _SLOT_HEIGHT
    )
)
DISPLAY_HEADER_3 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT, 
    bounds = DisplayBounds(
        x = 120, 
        y = 0, 
        w = _SLOT_WIDTH, 
        h = _SLOT_HEIGHT
    )
)
DISPLAY_HEADER_4 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT, 
    bounds = DisplayBounds(
        x = 180, 
        y = 0, 
        w = _SLOT_WIDTH, 
        h = _SLOT_HEIGHT
    )
)

DISPLAY_FOOTER_1 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT, 
    bounds = DisplayBounds(
        x = 0, 
        y = _FOOTER_Y2, 
        w = _SLOT_WIDTH, 
        h = _SLOT_HEIGHT
    )
)
DISPLAY_FOOTER_2 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT, 
    bounds = DisplayBounds(
        x = 60, 
        y = _FOOTER_Y2, 
        w = _SLOT_WIDTH, 
        h = _SLOT_HEIGHT
    )
)
DISPLAY_FOOTER_3 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT, 
    bounds = DisplayBounds(
        x = 120, 
        y = _FOOTER_Y2, 
        w = _SLOT_WIDTH, 
        h = _SLOT_HEIGHT
    )
)
DISPLAY_FOOTER_4 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT, 
    bounds = DisplayBounds(
        x = 180, 
        y = _FOOTER_Y2, 
        w = _SLOT_WIDTH, 
        h = _SLOT_HEIGHT
    )
)

Splashes = TunerDisplayCallback(
    splash_default = DisplayElement(
        bounds = DisplayBounds(
            x = 0, 
            y = 0, 
            w = _DISPLAY_WIDTH, 
            h = _DISPLAY_HEIGHT
        ), 
        children = [
            DISPLAY_HEADER_1,
            DISPLAY_HEADER_2,
            DISPLAY_HEADER_3,
            DISPLAY_HEADER_4,
            DISPLAY_FOOTER_1,
            DISPLAY_FOOTER_2,
            DISPLAY_FOOTER_3,
            DISPLAY_FOOTER_4,
            DisplayLabel(
                bounds = DisplayBounds(
                    x = 0, 
                    y = 60, 
                    w = _DISPLAY_WIDTH, 
                    h = _RIG_NAME_HEIGHT
                ), 
                layout = {
                    "font": "/fonts/PTSans-NarrowBold-40.pcf",
                    "lineSpacing": 0.8,
                    "maxTextWidth": 240,
                    "textColor": (255,255,255),
                    "backColor": (0,0,0),
                    "text": KemperRigNameCallback.DEFAULT_TEXT,
                    
                }, 
                callback = KemperRigNameCallback(
                    show_name = True, 
                    show_rig_id = True
                )
            ),
            BidirectionalProtocolState(
                DisplayBounds(
                    x = 0, 
                    y = _SLOT_HEIGHT, 
                    w = _DISPLAY_WIDTH, 
                    h = _RIG_NAME_HEIGHT
                )
            ),
            
        ]
    )
)
