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
    "gc": MockGC()
}):
    from lib.pyswitch.ui.StatisticalDisplays import StatisticalDisplays
    from lib.pyswitch.ui.elements.DisplayElement import DisplayBounds



class TestStatisticalDisplays(unittest.TestCase):

    def test_stat_display(self):
        # Must not throw
        StatisticalDisplays.STATS_DISPLAY(DisplayBounds(20, 30, 40, 50))


    def test_performance_dot(self):
        # Must not throw
        StatisticalDisplays.PERFORMANCE_DOT(DisplayBounds(20, 30, 40, 50))