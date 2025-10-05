import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

with patch.dict(sys.modules, {
    "displayio": MockDisplayIO(),
    "adafruit_display_text": MockAdafruitDisplayText(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "adafruit_midi.program_change": MockAdafruitMIDIProgramChange(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "gc": MockGC()
}):
    from pyswitch.ui.ui import DisplayBounds



class TestDisplayBounds(unittest.TestCase):

    def test_eq(self):
        self.assertEqual(DisplayBounds(20, 40, 100, 400), DisplayBounds(20, 40, 100, 400))
        self.assertNotEqual(DisplayBounds(21, 40, 100, 400), DisplayBounds(20, 40, 100, 400))
        self.assertNotEqual(DisplayBounds(20, 41, 100, 400), DisplayBounds(20, 40, 100, 400))
        self.assertNotEqual(DisplayBounds(20, 40, 100, 400), DisplayBounds(20, 40, 120, 400))
        self.assertNotEqual(DisplayBounds(20, 40, 100, 400), DisplayBounds(20, 40, 100, 420))

    def test_clone(self):
        b = DisplayBounds(20, 40, 100, 400)
        c = b.clone()
        self.assertEqual(b, c)
        c.x = 33
        self.assertEqual(b.x, 20)
        self.assertNotEqual(b, c)

