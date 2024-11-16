import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

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
    from .mocks_appl import *
    from lib.pyswitch.controller.ConditionTree import PushButtonCondition


class TestConditionPushButton(unittest.TestCase):


    def test_functionality(self):
        action_1 = MockAction({ "id": "bar" })
        action_2 = MockAction({ "id": "foo" })
        action_3 = MockAction()
        action_4 = MockAction()
        period = MockPeriodCounter()

        condition_1 = PushButtonCondition(
            action = action_2,
            enabled = [
                action_3
            ],
            disabled = [
                action_4
            ]
        )

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            midi = MockMidiController(),
            switches = [
                {
                    "assignment": {
                        "model": MockSwitch()
                    },
                    "actions": [
                        condition_1,                        
                        action_1,
                        action_2                        
                    ]
                }
            ],
            period_counter = period
        )

        # Build scene:
        # Step 1
        def prep1():
            period.exceed_next_time = True
            
        def eval1():
            self.assertEqual(condition_1.true, False)
            return True

        # Step 2
        def prep2():
            period.exceed_next_time = True

            action_2.state = True
            
        def eval2():
            self.assertEqual(condition_1.true, True)
            return True
        
        # Step 3
        def prep3():
            period.exceed_next_time = True

        def eval3():
            return True
        
        # Step 4
        def prep4():
            period.exceed_next_time = True


        def eval4():
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


#############################################################################


    #def test_update_not_initialized(self):
    #    action_3 = MockAction()
    #    action_4 = MockAction()
        
    #    condition_1 = PushButtonCondition(
    #        action = MockAction(),
    #        enabled = [
    #            action_3
    #        ],
    #        disabled = [
    #            action_4
    #        ]
    #    )

    #    with self.assertRaises(Exception):
    #        condition_1.update()