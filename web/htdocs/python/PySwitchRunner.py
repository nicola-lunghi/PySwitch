import sys
from unittest.mock import patch

from pyodide.ffi.wrappers import set_timeout
from js import externalRefs

from mocks import *
from wrappers.WrapDisplayDriver import *
from wrappers.wrap_circuitpy import *
from wrappers.wrap_adafruit_display import *
from wrappers.wrap_adafruit_led import *
from wrappers.wrap_adafruit_midi import *

class PySwitchRunner:
    def __init__(self, container_id, dom_namespace, update_interval_ms):
        self.container_id = container_id

        self.dom_namespace = dom_namespace
        self.update_interval_ms = update_interval_ms
        self.running = False
        self.__protocol_state = None
        
    # Set up a PySwitch controller and let it run
    def run(self):
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
            "rotaryio": WrapRotaryIO(self.dom_namespace)
        }):            
            self.display_driver = WrapDisplayDriver(
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

            from PySwitchDevice import PySwitchDevice
            self.device = PySwitchDevice(self.container_id, self.dom_namespace)
            self.device.init(Inputs, Splashes)

            midi_in = WrapMidiInput()
            midi_out = WrapMidiOutput()

            midi = AdafruitUsbMidiDevice(
                port_in = midi_in,
                port_out = midi_out,
                in_buf_size = 100
            )

            protocol = KemperBidirectionalProtocol(
                time_lease_seconds = 30
            )

            # Controller instance (runs the processing loop and keeps everything together)
            self.controller = Controller(
                led_driver = WrapNeoPixelDriver(self.dom_namespace), 
                protocol = protocol,
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
                    # "updateInterval": 2000,
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
                
        self.running = True

        # Local callback for set_timeout
        def tick():            
            if self.running:
                set_timeout(tick, self.update_interval_ms)
            
            #print(repr(self) + " tick")

            self.controller.tick()
            self.display_driver.update()

            externalRefs.protocolState = protocol.state

            # # Notify when the bidirectional protocol state has been changed
            # if protocol.state != self.__protocol_state:
            #     self.__protocol_state = protocol.state

            #     if externalRefs.stateCallback:
            #         externalRefs.stateCallback(protocol.state);


        tick()

    # Stop execution
    def stop(self):        
        self.running = False


    

