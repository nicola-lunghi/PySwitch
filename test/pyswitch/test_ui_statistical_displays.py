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
    from lib.pyswitch.ui.elements import PERFORMANCE_DOT, BIDIRECTIONAL_PROTOCOL_STATE_DOT
    from lib.pyswitch.ui.ui import DisplayBounds



class TestStatisticalDisplays(unittest.TestCase):

    #def test_stat_display(self):
    #    # Must not throw
    #    STATS_DISPLAY(DisplayBounds(20, 30, 40, 50))


    def test_performance_dot(self):
        # Must not throw
        PERFORMANCE_DOT(DisplayBounds(20, 30, 40, 50))


    def test_protocol_dot(self):
        # Must not throw
        BIDIRECTIONAL_PROTOCOL_STATE_DOT(DisplayBounds(20, 30, 40, 50))