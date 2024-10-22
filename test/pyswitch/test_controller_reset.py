import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

# Import subject under test
with patch.dict(sys.modules, {
    "usb_midi": MockUsbMidi(),
    "adafruit_midi": MockAdafruitMIDI(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "gc": MockGC()
}):
    #from lib.pyswitch.controller.Controller import Controller
    from .mocks_appl import *
    from lib.pyswitch.misc import Updateable


class MockUpdateable(Updateable):
    pass

class TestControllerReset(unittest.TestCase):

    def test_reset_switches(self):
        switch_1 = MockSwitch()
        switch_2 = MockSwitch()
        
        action_1 = MockAction()
        action_2 = MockAction()
        action_3 = MockAction()

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            value_provider = MockValueProvider(),
            switches = [
                {
                    "assignment": {
                        "model": switch_1
                    },
                    "actions": [
                        action_1                        
                    ]
                },
                {
                    "assignment": {
                        "model": switch_2
                    },
                    "actions": [
                        action_2,
                        action_3
                    ]
                }
            ]
        )

        appl.add_updateable(MockUpdateable())

        appl.reset_switches()

        self.assertEqual(action_1.num_reset_calls, 1)
        self.assertEqual(action_2.num_reset_calls, 1)
        self.assertEqual(action_3.num_reset_calls, 1)

        appl.reset_switches([appl.switches[0]])

        self.assertEqual(action_1.num_reset_calls, 1)
        self.assertEqual(action_2.num_reset_calls, 2)
        self.assertEqual(action_3.num_reset_calls, 2)

