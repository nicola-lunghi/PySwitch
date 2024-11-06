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
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "gc": MockGC()
}):
    #from lib.pyswitch.controller.Controller import Controller
    from .mocks_appl import *


class TestControllerActions(unittest.TestCase):

    def test_update_period(self):
        switch_1 = MockSwitch()
        switch_2 = MockSwitch()
        
        action_1 = MockAction()
        action_2 = MockAction()
        action_3 = MockAction()

        period = MockPeriodCounter()

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            communication = {
                "valueProvider": MockValueProvider()
            },
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

        # Build scene:
        # Step 1: Not exceeded
        def prep1():
            self.assertEqual(period.exceed_next_time, False)
            self.assertEqual(action_1.num_update_calls_overall, 0)
            self.assertEqual(action_2.num_update_calls_overall, 0)
            self.assertEqual(action_3.num_update_calls_overall, 0)

        def eval1():
            self.assertEqual(period.exceed_next_time, False)
            self.assertEqual(action_1.num_update_calls_overall, 0)
            self.assertEqual(action_2.num_update_calls_overall, 0)
            self.assertEqual(action_3.num_update_calls_overall, 0)
            return True

        # Step 2: Exceeded the first time
        def prep2():
            period.exceed_next_time = True
            self.assertEqual(action_1.num_update_calls_overall, 0)
            self.assertEqual(action_2.num_update_calls_overall, 0)
            self.assertEqual(action_3.num_update_calls_overall, 0)

        def eval2():
            self.assertEqual(period.exceed_next_time, False)
            self.assertEqual(action_1.num_update_calls_overall, 1)
            self.assertEqual(action_2.num_update_calls_overall, 1)
            self.assertEqual(action_3.num_update_calls_overall, 1)
            return True
        
        # Step 3: Not exceeded
        def prep3():
            self.assertEqual(period.exceed_next_time, False)
            self.assertEqual(action_1.num_update_calls_overall, 1)
            self.assertEqual(action_2.num_update_calls_overall, 1)
            self.assertEqual(action_3.num_update_calls_overall, 1)

        def eval3():
            self.assertEqual(period.exceed_next_time, False)
            self.assertEqual(action_1.num_update_calls_overall, 1)
            self.assertEqual(action_2.num_update_calls_overall, 1)
            self.assertEqual(action_3.num_update_calls_overall, 1)
            return True
        
        # Step 4: Exceeded again
        def prep4():
            period.exceed_next_time = True
            self.assertEqual(action_1.num_update_calls_overall, 1)
            self.assertEqual(action_2.num_update_calls_overall, 1)
            self.assertEqual(action_3.num_update_calls_overall, 1)

        def eval4():
            self.assertEqual(period.exceed_next_time, False)
            self.assertEqual(action_1.num_update_calls_overall, 2)
            self.assertEqual(action_2.num_update_calls_overall, 2)
            self.assertEqual(action_3.num_update_calls_overall, 2)
            return False

        # Build scenes hierarchy
        appl.next_step = SceneStep(
            num_pass_ticks = 5,
            prepare = prep1,
            evaluate = eval1,

            next = SceneStep(
                num_pass_ticks = 5,
                prepare = prep2,
                evaluate = eval2,
            
                next = SceneStep(
                    num_pass_ticks = 5,
                    prepare = prep3,
                    evaluate = eval3,
            
                    next = SceneStep(
                        num_pass_ticks = 5,
                        prepare = prep4,
                        evaluate = eval4
                    )
                )
            )
        )

        # Run process
        appl.process()

        