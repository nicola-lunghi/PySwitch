import sys
from unittest.mock import patch

from browser.timer import *
from browser import console

from mocks.mocks_lib import *
from mocks.mocks_adafruit import *
from mocks.mocks_circuitpy import *

from mocks.display.WebDisplayDriver import WebDisplayDriver

with patch.dict(sys.modules, {
	"micropython": MockMicropython,
	"gc": MockGC(),
	"board": MockBoard,
    "adafruit_midi": MockAdafruitMIDI(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "adafruit_midi.program_change": MockAdafruitMIDIProgramChange(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "displayio": MockDisplayIO(),
    #"adafruit_display_text": MockAdafruitDisplayText(),
    "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
    "busio": MockBusIO(),
    "adafruit_misc.adafruit_st7789": MockAdafruit_ST7789,
    "adafruit_misc.neopixel": MockNeoPixel,
    # "adafruit_bitmap_font": MockAdafruitBitmapFont,
    "fontio": MockFontIO(),
    "digitalio": MockDigitalIO,
    "fontio": MockFontIO(),
    "bitmaptools": MockBitmapTools,
    "io": MockIO
}):
    from mocks.mocks_adafruit_display import *

    # Initialize Display first to get console output on setup/config errors (for users who do not connect to the serial console)
    display_driver = WebDisplayDriver()
    display_driver.init()

    from pyswitch.controller.Controller import Controller
    from pyswitch.controller.MidiController import MidiController
    from pyswitch.ui.UiController import UiController

    from pyswitch.clients.kemper import KemperBidirectionalProtocol
    
    from display import Splashes
    from inputs import Inputs

    # Controller instance (runs the processing loop and keeps everything together)
    controller = Controller(
        led_driver = MockNeoPixelDriver(), 
        protocol = KemperBidirectionalProtocol(
            time_lease_seconds = 30
        ),
        midi = MidiController(
            routings = {}
        ),
        config = {},
        inputs = Inputs,
        ui = UiController(
            display_driver = display_driver,
            font_loader = MockAdafruitFontLoader(),
            splash_callback = Splashes
        )
    )

    # Prepare to run the processing loop
    controller.init()
    controller.tick()
    
    def tick():
        console.log("tick")
        controller.tick()

    # Start processing loop (done here to keep the call stack short)
    set_interval(tick, 5)
    #while _controller.tick():
    #    pass
