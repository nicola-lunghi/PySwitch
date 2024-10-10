import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks import *

# Import subject under test
with patch.dict(sys.modules, {
    "usb_midi": MockUsbMidi(),
    "adafruit_midi": MockAdafruitMIDI(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "gc": MockGC()
}):
    from lib.pyswitch.controller.Controller import Controller


class TestScenarios(unittest.TestCase):

    #################################################################################################

    # Minimal call: Must not throw anything
    def test_minimal(self):
        appl = Controller(
            led_driver = MockNeoPixelDriver(),
            config = {},
            value_provider = MockValueProvider(),
            switches = [],
            displays = [],
            ui = None            
        )
        
    #################################################################################################

    
