import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.
import coverage

from .mocks_lib import *

# Import subject under test
with patch.dict(sys.modules, {
    "usb_midi": MockUsbMidi(),
    "adafruit_midi": MockAdafruitMIDI(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "gc": MockGC()
}):
    from .mocks_appl import *    
    from lib.pyswitch.controller.Controller import Controller


class TestScenarios(unittest.TestCase):

    #################################################################################################

    # Minimal call: Must not throw anything
    def test_minimal(self):
        led_driver = MockNeoPixelDriver()

        appl = Controller(
            led_driver = led_driver,
            config = {},
            value_provider = MockValueProvider(),
            switches = [],
            displays = [],
            ui = None            
        )

        self.assertEqual(len(led_driver.leds), 0)
        
    #################################################################################################

    def test_switches_1(self):
        led_driver = MockNeoPixelDriver()

        appl = Controller(
            led_driver = led_driver,
            config = {},
            value_provider = MockValueProvider(),
            switches = [
                {
                    "assignment": {
                        "model": MockSwitch(),
                        "pixels": (0, 1, 2, 3, 8)
                    },
                    "actions": [
                        MockAction()
                    ]
                }
            ],
            displays = [],
            ui = None
        )

        self.assertEqual(len(led_driver.leds), 9)
        
    
