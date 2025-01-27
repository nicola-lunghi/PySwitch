import sys
from unittest.mock import patch

from pyodide.ffi.wrappers import set_timeout

from mocks.mocks_lib import *
from mocks.mocks_adafruit_led import *
from mocks.mocks_adafruit_midi import *
from mocks.mocks_adafruit_display import *
from mocks.mocks_circuitpy import *

from mocks.display.WebDisplayDriver import WebDisplayDriver

class PyRunner:
    def __init__(self, dom_namespace, update_interval_ms):
        self.dom_namespace = dom_namespace
        self.update_interval_ms = update_interval_ms
        
    def init(self):
        with patch.dict(sys.modules, {
            "micropython": MockMicropython,
            "gc": MockGC(),
            "board": MockBoard,
            "displayio": MockDisplayIO(),
            "adafruit_display_text": MockAdafruitDisplayText,
            "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
            "busio": MockBusIO(),
            "adafruit_misc.adafruit_st7789": MockAdafruit_ST7789,
            "adafruit_misc.neopixel": MockNeoPixel,
            "adafruit_bitmap_font": MockAdafruitBitmapFont,
            "fontio": MockFontIO(),
            "digitalio": MockDigitalIO
        }):
            self.display_driver = WebDisplayDriver(
                width = 240,
                height = 240,
                dom_namespace = self.dom_namespace
            )
            self.display_driver.init()

            from pyswitch.controller.Controller import Controller
            from pyswitch.controller.MidiController import MidiController, MidiRouting
            from pyswitch.ui.UiController import UiController
            from pyswitch.hardware.adafruit.AdafruitUsbMidiDevice import AdafruitUsbMidiDevice

            from pyswitch.clients.kemper import KemperBidirectionalProtocol

            from display import Splashes
            from inputs import Inputs

            midi_in = MockMidiInput()
            midi_out = MockMidiOutput()

            midi = AdafruitUsbMidiDevice(
                port_in = midi_in,
                port_out = midi_out,
                in_buf_size = 100
            )

            # Controller instance (runs the processing loop and keeps everything together)
            self.controller = Controller(
                led_driver = MockNeoPixelDriver(self.dom_namespace), 
                protocol = KemperBidirectionalProtocol(
                    time_lease_seconds = 30
                ),
                midi = MidiController(
                    routings = {
                        # Application: Receive MIDI messages from USB
                        MidiRouting(
                            source = midi,
                            target = MidiRouting.APPLICATION
                        ),

                        # Application: Send MIDI messages to USB
                        MidiRouting(
                            source = MidiRouting.APPLICATION,
                            target = midi
                        ),
                    }
                ),
                config = {
                    "debugBidirectionalProtocol": True,
                    "ledBrightnessOn": 1,
                    "ledBrightnessOff": 0.4
                },
                inputs = Inputs,
                ui = UiController(
                    display_driver = self.display_driver,
                    font_loader = MockAdafruitFontLoader(),
                    splash_callback = Splashes
                )
            )

            # Prepare to run the processing loop
            self.controller.init()
                
        # Local callback for set_timeout
        def tick():
            set_timeout(tick, self.update_interval_ms)
            
            self.controller.tick()
            self.display_driver.update()

        tick()

