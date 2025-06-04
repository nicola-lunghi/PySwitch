from micropython import const
from pyswitch.ui.ui import DisplayElement, DisplayBounds
from pyswitch.ui.elements import DisplayLabel, BidirectionalProtocolState
from pyswitch.clients.kemper import KemperRigNameCallback, TunerDisplayCallback



_DISPLAY_WIDTH = const(240)
_DISPLAY_HEIGHT = const(240)
_SLOT_HEIGHT = const(40)
_RIG_ID_HEIGHT = const(40)
_RIG_NAME_HEIGHT = const(160)
_RIG_ID_Y = const(190)


Splashes = TunerDisplayCallback(
    strobe = False,
    splash_default = DisplayElement(
        bounds = DisplayBounds(0, 0, _DISPLAY_WIDTH, _DISPLAY_HEIGHT),
        children = [
            DisplayLabel(
                bounds = DisplayBounds(
                    0, 
                    _SLOT_HEIGHT,
                    _DISPLAY_WIDTH,
                    _RIG_NAME_HEIGHT
                ),

                layout = {
                    "font": "/fonts/PTSans-NarrowBold-40.pcf",
                    "lineSpacing": 0.8,
                    "maxTextWidth": 220,
                    "text": KemperRigNameCallback.DEFAULT_TEXT,
                },

                callback = KemperRigNameCallback(
                    show_name = True,
                    show_rig_id = False
                )
            ),

            DisplayLabel(
                bounds = DisplayBounds(
                    0,
                    _RIG_ID_Y,
                    _DISPLAY_WIDTH,
                    _RIG_ID_HEIGHT
                ),

                layout = {
                    "font": "/fonts/PTSans-NarrowBold-40.pcf",
                },

                callback = KemperRigNameCallback(
                    show_name = False,
                    show_rig_id = True
                )
            ),

            BidirectionalProtocolState(DisplayBounds(
                0, 
                _SLOT_HEIGHT,
                _DISPLAY_WIDTH,
                _RIG_NAME_HEIGHT
            ))
        ]
    )
)
