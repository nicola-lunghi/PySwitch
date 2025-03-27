import sys
from unittest.mock import patch
import traceback

from pyodide.ffi.wrappers import set_timeout
from js import externalRefs

from mocks import *
from wrappers.WrapDisplayDriver import *
from wrappers.wrap_io import *
from wrappers.wrap_adafruit_display import *
from wrappers.wrap_adafruit_led import *
from wrappers.wrap_adafruit_midi import *
from wrappers.wrap_time import *
from wrappers.wrap_hid import *

class PySwitchRunner:
    def __init__(self, container_id, dom_namespace, update_interval_ms, coverage):
        self.container_id = container_id

        self.dom_namespace = dom_namespace
        self.update_interval_ms = update_interval_ms
        self.coverage = coverage

        self.running = False
        self.triggerStop = False

        self.protocol = None
        self.frontend = None        

    # Set up a PySwitch controller and let it run
    def run(self):
        self.running = True
        self.triggerStop = False

        self.init()

    def init(self):
        if self.coverage:
            import coverage

            cov = coverage.Coverage()
            cov.start()

        with patch.dict(sys.modules, {
            "micropython": MockMicropython,
            "gc": MockGC(),
            "board": WrapBoard,
            "displayio": WrapDisplayIO(),
            "adafruit_display_text": WrapAdafruitDisplayText(self.dom_namespace),
            "adafruit_display_shapes.rect": WrapDisplayShapes().rect(),
            "busio": MockBusIO(),
            "adafruit_misc.adafruit_st7789": MockAdafruit_ST7789,
            "adafruit_misc.neopixel": MockNeoPixel,
            "adafruit_bitmap_font": MockAdafruitBitmapFont,
            "fontio": MockFontIO(),
            "digitalio": WrapDigitalIO(self.dom_namespace),
            "analogio": WrapAnalogIO(self.dom_namespace),
            "rotaryio": WrapRotaryIO(self.dom_namespace),
            "time": WrapTime(),
            "usb_hid": WrapUsbHid(),
            "adafruit_hid.keyboard": WrapUsbHidKeyboard
        }):            
            self.display_driver = WrapDisplayDriver(
                width = 240,
                height = 240,
                dom_namespace = self.dom_namespace
            )
            self.display_driver.init()

            from pyswitch.controller import Controller
            from pyswitch.controller.midi import MidiController, MidiRouting
            from pyswitch.ui.UiController import UiController
            from pyswitch.hardware.adafruit.AdafruitUsbMidiDevice import AdafruitUsbMidiDevice

            from pyswitch.clients.kemper import KemperBidirectionalProtocol

            from display import Splashes
            from inputs import Inputs

            midi_in = WrapMidiInput()
            midi_out = WrapMidiOutput()

            midi = AdafruitUsbMidiDevice(
                port_in = midi_in,
                port_out = midi_out,
                in_buf_size = 100
            )

            self.protocol = KemperBidirectionalProtocol(
                time_lease_seconds = 30
            )

            # Controller instance (runs the processing loop and keeps everything together)
            self.controller = Controller(
                led_driver = WrapNeoPixelDriver(self.dom_namespace), 
                protocol = self.protocol,
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
                    # "debugBidirectionalProtocol": True,
                    # "updateInterval": 2000,
                    # "debugSentMessages": True
                },
                inputs = Inputs,
                ui = UiController(
                    display_driver = self.display_driver,
                    font_loader = WrapFontLoader(),
                    splash_callback = Splashes
                )
            )

            # Prepare to run the processing loop
            self.controller.init()
                
        # Local callback for set_timeout
        def tick():            
            if not self.triggerStop:
                set_timeout(tick, self.update_interval_ms)

                self.tick()
            else:
                self.running = False

        if self.running:
            tick()

        if self.coverage:
            cov.stop()
            cov.save()
            # print(cov.get_data())

    # One tick of the controller
    def tick(self):
        try:
            self.controller.tick()
        
        except Exception as exc:
            self.stop()

            if hasattr(externalRefs, "errorHandler"):
                externalRefs.errorHandler.handle("".join(traceback.format_exception(exc)))
            
            raise exc
        
        self.display_driver.update()

        externalRefs.protocolState = self.protocol.state

    # Stop execution of the set_timeout handler by just not renewing it
    def stop(self):        
        self.triggerStop = True


    

