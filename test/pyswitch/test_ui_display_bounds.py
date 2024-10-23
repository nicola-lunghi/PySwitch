import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

with patch.dict(sys.modules, {
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
}):
    from lib.pyswitch.ui.elements.DisplayElement import DisplayBounds



class TestDisplayBounds(unittest.TestCase):

    def test_eq(self):
        self.assertEqual(DisplayBounds(20, 40, 100, 400), DisplayBounds(20, 40, 100, 400))
        self.assertNotEqual(DisplayBounds(21, 40, 100, 400), DisplayBounds(20, 40, 100, 400))
        self.assertNotEqual(DisplayBounds(20, 41, 100, 400), DisplayBounds(20, 40, 100, 400))
        self.assertNotEqual(DisplayBounds(20, 40, 100, 400), DisplayBounds(20, 40, 120, 400))
        self.assertNotEqual(DisplayBounds(20, 40, 100, 400), DisplayBounds(20, 40, 100, 420))

    def test_repr(self):
        self.assertIn(repr((20, 40, 100, 400)), repr(DisplayBounds(20, 40, 100, 400)))

    def test_clone(self):
        b = DisplayBounds(20, 40, 100, 400)
        c = b.clone()
        self.assertEqual(b, c)
        c.x = 33
        self.assertEqual(b.x, 20)
        self.assertNotEqual(b, c)

    def test_empty(self):
        self.assertEqual(DisplayBounds(20, 40, 100, 400).empty, False)
        self.assertEqual(DisplayBounds(20, 40, 0, 400).empty, True)
        self.assertEqual(DisplayBounds(20, 40, 100, 0).empty, True)

    def test_remove_top(self):
        b = DisplayBounds(20, 40, 100, 400)
        
        self.assertEqual(b.remove_from_top(20), DisplayBounds(20, 40, 100, 20))
        self.assertEqual(b, DisplayBounds(20, 60, 100, 380))

    def test_remove_bottom(self):
        b = DisplayBounds(20, 40, 100, 400)
        
        self.assertEqual(b.remove_from_bottom(20), DisplayBounds(20, 420, 100, 20))
        self.assertEqual(b, DisplayBounds(20, 40, 100, 380))

    def test_remove_left(self):
        b = DisplayBounds(20, 40, 100, 400)
        
        self.assertEqual(b.remove_from_left(20), DisplayBounds(20, 40, 20, 400))
        self.assertEqual(b, DisplayBounds(40, 40, 80, 400))

    def test_remove_right(self):
        b = DisplayBounds(20, 40, 100, 400)
        
        self.assertEqual(b.remove_from_right(20), DisplayBounds(100, 40, 20, 400))
        self.assertEqual(b, DisplayBounds(20, 40, 80, 400))

    def test_translate(self):
        b = DisplayBounds(20, 40, 100, 400)

        b.translate(-2, 4)
        self.assertEqual(b, DisplayBounds(18, 44, 100, 400))

        b.translate(20, -10)
        self.assertEqual(b, DisplayBounds(38, 34, 100, 400))

    def test_translated(self):
        b = DisplayBounds(20, 40, 100, 400)

        self.assertEqual(b.translated(-2, 4), DisplayBounds(18, 44, 100, 400))
        self.assertEqual(b, DisplayBounds(20, 40, 100, 400))

    def test_with_position(self):
        b = DisplayBounds(20, 40, 100, 400)

        self.assertEqual(b.with_position(3, 5), DisplayBounds(3, 5, 100, 400))
        self.assertEqual(b, DisplayBounds(20, 40, 100, 400))

    def test_top(self):
        b = DisplayBounds(20, 40, 100, 400)
        
        self.assertEqual(b.top(20), DisplayBounds(20, 40, 100, 20))
        self.assertEqual(b, DisplayBounds(20, 40, 100, 400))

    def test_bottom(self):
        b = DisplayBounds(20, 40, 100, 400)
        
        self.assertEqual(b.bottom(20), DisplayBounds(20, 420, 100, 20))
        self.assertEqual(b, DisplayBounds(20, 40, 100, 400))

    def test_left(self):
        b = DisplayBounds(20, 40, 100, 400)
        
        self.assertEqual(b.left(20), DisplayBounds(20, 40, 20, 400))
        self.assertEqual(b, DisplayBounds(20, 40, 100, 400))

    def test_right(self):
        b = DisplayBounds(20, 40, 100, 400)
        
        self.assertEqual(b.right(20), DisplayBounds(100, 40, 20, 400))
        self.assertEqual(b, DisplayBounds(20, 40, 100, 400))