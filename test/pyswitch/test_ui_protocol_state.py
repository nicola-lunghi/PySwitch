import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

with patch.dict(sys.modules, {
    "displayio": MockDisplayIO(),
    "adafruit_display_text": MockAdafruitDisplayText(),
    "usb_midi": MockUsbMidi(),
    "adafruit_midi": MockAdafruitMIDI(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "gc": MockGC()
}):
    #from adafruit_midi.system_exclusive import SystemExclusive

    from lib.pyswitch.ui.ui import DisplayBounds
    from lib.pyswitch.ui.elements import BidirectionalProtocolState
    from lib.pyswitch.controller.Client import BidirectionalClient
    
    from .mocks_appl import MockBidirectionalProtocol, MockMidiController, MockValueProvider, MockClient
    from .mocks_ui import MockDisplaySplash
    

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
                value_provider = MockValueProvider(), 
                protocol = protocol
            )
        )

        ui = MockDisplaySplash()

        with patch.dict(sys.modules, {
            "adafruit_display_shapes.circle": MockDisplayShapes().circle()
        }):
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

        ui = MockDisplaySplash()

        with patch.dict(sys.modules, {
            "adafruit_display_shapes.circle": MockDisplayShapes().circle()
        }):
            display.init(ui, appl)

        display.update()
        




