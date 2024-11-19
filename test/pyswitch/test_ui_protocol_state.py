import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

with patch.dict(sys.modules, {
    "micropython": MockMicropython,
    "displayio": MockDisplayIO(),
    "adafruit_display_text": MockAdafruitDisplayText(),
    "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
    "usb_midi": MockUsbMidi(),
    "adafruit_midi": MockAdafruitMIDI(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "adafruit_midi.program_change": MockAdafruitMIDIProgramChange(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "gc": MockGC()
}):
    #from adafruit_midi.system_exclusive import SystemExclusive

    from lib.pyswitch.ui.ui import DisplayBounds, DisplayElement
    from lib.pyswitch.ui.elements import BidirectionalProtocolState
    from lib.pyswitch.controller.Client import BidirectionalClient
    
    from .mocks_appl import MockBidirectionalProtocol, MockMidiController, MockClient
    

class MockController:
    def __init__(self, client):
        self.client = client


class TestProtocolState(unittest.TestCase):

    def test(self):
        display = BidirectionalProtocolState(
            bounds = DisplayBounds(22, 33, 44, 55)
        )

        self.assertEqual(display.bounds, DisplayBounds(22, 33, 44, 55))

        protocol = MockBidirectionalProtocol()        

        appl = MockController(
            client = BidirectionalClient(
                midi = MockMidiController(), 
                config = {}, 
                protocol = protocol
            )
        )

        ui = DisplayElement()
        ui.make_splash(None)

        display.init(ui, appl)

        protocol.output_color = (2, 5, 6)
        display.update()
        self.assertEqual(display._dot.fill, (2, 5, 6))

        protocol.output_color = (11, 45, 66)
        display.update()
        self.assertEqual(display._dot.fill, (11, 45, 66))

        display.update()
        self.assertEqual(display._dot.fill, (11, 45, 66))
    
    def test_no_protocol(self):
        display = BidirectionalProtocolState(
            bounds = DisplayBounds(22, 33, 44, 55)
        )

        appl = MockController(
            client = MockClient()
        )

        ui = DisplayElement()
        ui.make_splash(None)

        display.init(ui, appl)

        display.update()
        




