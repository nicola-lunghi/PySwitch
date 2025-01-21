import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

# Import subject under test
with patch.dict(sys.modules, {
    "micropython": MockMicropython,
    "usb_midi": MockUsbMidi(),
    "adafruit_midi": MockAdafruitMIDI(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "adafruit_midi.program_change": MockAdafruitMIDIProgramChange(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "gc": MockGC()
}):
    from lib.pyswitch.controller.Controller import Controller
    from .mocks_appl import *


class TestControllerActions(unittest.TestCase):

    def test_update_period(self):
        switch_1 = MockSwitch()
        switch_2 = MockSwitch()
        
        action_1 = MockAction()
        action_2 = MockAction()
        action_3 = MockAction()

        period = MockPeriodCounter()

        appl = Controller(
            led_driver = MockNeoPixelDriver(),
            midi = MockMidiController(),
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
            ],
            period_counter = period
        )

        appl.init()

        # Build scene:
        # Step 1: Not exceeded
        self.assertEqual(period.exceed_next_time, False)
        self.assertEqual(action_1.num_update_calls_overall, 0)
        self.assertEqual(action_2.num_update_calls_overall, 0)
        self.assertEqual(action_3.num_update_calls_overall, 0)

        appl.tick()
        appl.tick()
        
        self.assertEqual(period.exceed_next_time, False)
        self.assertEqual(action_1.num_update_calls_overall, 0)
        self.assertEqual(action_2.num_update_calls_overall, 0)
        self.assertEqual(action_3.num_update_calls_overall, 0)
        
        # Step 2: Exceeded the first time
        period.exceed_next_time = True
        self.assertEqual(action_1.num_update_calls_overall, 0)
        self.assertEqual(action_2.num_update_calls_overall, 0)
        self.assertEqual(action_3.num_update_calls_overall, 0)

        appl.tick()
        appl.tick()
        
        self.assertEqual(period.exceed_next_time, False)
        self.assertEqual(action_1.num_update_calls_overall, 1)
        self.assertEqual(action_2.num_update_calls_overall, 1)
        self.assertEqual(action_3.num_update_calls_overall, 1)
        
        # Step 3: Not exceeded
        self.assertEqual(period.exceed_next_time, False)
        self.assertEqual(action_1.num_update_calls_overall, 1)
        self.assertEqual(action_2.num_update_calls_overall, 1)
        self.assertEqual(action_3.num_update_calls_overall, 1)

        appl.tick()
        appl.tick()
        
        self.assertEqual(period.exceed_next_time, False)
        self.assertEqual(action_1.num_update_calls_overall, 1)
        self.assertEqual(action_2.num_update_calls_overall, 1)
        self.assertEqual(action_3.num_update_calls_overall, 1)
        
        # Step 4: Exceeded again
        period.exceed_next_time = True
        self.assertEqual(action_1.num_update_calls_overall, 1)
        self.assertEqual(action_2.num_update_calls_overall, 1)
        self.assertEqual(action_3.num_update_calls_overall, 1)

        appl.tick()
        appl.tick()
        
        self.assertEqual(period.exceed_next_time, False)
        self.assertEqual(action_1.num_update_calls_overall, 2)
        self.assertEqual(action_2.num_update_calls_overall, 2)
        self.assertEqual(action_3.num_update_calls_overall, 2)
        
        