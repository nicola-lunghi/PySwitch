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
    "adafruit_midi.start": MockAdafruitMIDIStart(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "gc": MockGC()
}):
    #from lib.pyswitch.controller.Controller import Controller
    from .mocks_appl import *
    from lib.pyswitch.controller.ConditionTree import ConditionTree
    from lib.pyswitch.controller.actions.actions import HoldAction


class TestControllerConditions(unittest.TestCase):

    def test_actions_flat_conditions(self):
        switch_1 = MockSwitch()
        switch_2 = MockSwitch()
        switch_3 = MockSwitch()
        
        action_1 = MockAction()
        action_2 = MockAction()
        action_3 = MockAction()
        action_4 = MockAction()

        period = MockPeriodCounter()

        condition_1 = MockCondition(
            yes = [
                action_2
            ],
            no = [
                action_3
            ]
        )

        condition_2 = MockCondition(
            yes = [
                action_1
            ]
        )

        condition_3 = MockCondition(
            no = [
                action_4
            ]
        )

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
                    "actions": condition_1
                },
                {
                    "assignment": {
                        "model": switch_2
                    },
                    "actions": condition_2
                },
                {
                    "assignment": {
                        "model": switch_3
                    },
                    "actions": condition_3
                }
            ],
            period_counter = period
        )

        # Build scene:
        # Step 1: Condition is true
        def prep1():
            period.exceed_next_time = True
            
            self.assertEqual(condition_1.true, True)
            self.assertEqual(condition_1.num_update_calls, 0)

            self.assertEqual(condition_2.true, True)
            self.assertEqual(condition_2.num_update_calls, 0)
            
            self.assertEqual(condition_3.true, True)
            self.assertEqual(condition_3.num_update_calls, 0)

            self.assertEqual(action_1.num_update_calls_enabled, 0)
            self.assertEqual(action_2.num_update_calls_enabled, 0)
            self.assertEqual(action_3.num_update_calls_enabled, 0)
            self.assertEqual(action_4.num_update_calls_enabled, 0)

        def eval1():
            self.assertEqual(condition_1.true, True)

            self.assertEqual(condition_1.num_update_calls, 1)
            self.assertEqual(condition_2.num_update_calls, 1)
            self.assertEqual(condition_3.num_update_calls, 1)

            self.assertEqual(action_1.num_update_calls_enabled, 1)            
            self.assertEqual(action_2.num_update_calls_enabled, 1)
            self.assertEqual(action_3.num_update_calls_enabled, 0)
            self.assertEqual(action_4.num_update_calls_enabled, 0)
            return True

        # Step 2: Condition is false
        def prep2():
            period.exceed_next_time = True            
            condition_1.bool_value = False
            condition_2.bool_value = False
            condition_3.bool_value = False
            
            self.assertEqual(condition_1.true, True)
            self.assertEqual(condition_1.num_update_calls, 1)

            self.assertEqual(condition_2.true, True)
            self.assertEqual(condition_2.num_update_calls, 1)
            
            self.assertEqual(condition_3.true, True)
            self.assertEqual(condition_3.num_update_calls, 1)

            self.assertEqual(action_1.num_update_calls_enabled, 1)
            self.assertEqual(action_2.num_update_calls_enabled, 1)
            self.assertEqual(action_3.num_update_calls_enabled, 0)
            self.assertEqual(action_4.num_update_calls_enabled, 0)

        def eval2():
            self.assertEqual(condition_1.true, False)
            self.assertEqual(condition_2.true, False)
            self.assertEqual(condition_2.true, False)

            self.assertEqual(condition_1.num_update_calls, 2)
            self.assertEqual(condition_2.num_update_calls, 2)
            self.assertEqual(condition_3.num_update_calls, 2)

            self.assertEqual(action_1.num_update_calls_enabled, 1)
            self.assertEqual(action_2.num_update_calls_enabled, 1)
            self.assertEqual(action_3.num_update_calls_enabled, 1)
            self.assertEqual(action_4.num_update_calls_enabled, 1)
            return True
        
        # Step 3: True again
        def prep3():
            period.exceed_next_time = True
            condition_1.bool_value = True
            condition_2.bool_value = True
            condition_3.bool_value = True

            self.assertEqual(condition_1.true, False)
            self.assertEqual(condition_1.num_update_calls, 2)

            self.assertEqual(condition_2.true, False)
            self.assertEqual(condition_2.num_update_calls, 2)

            self.assertEqual(condition_3.true, False)
            self.assertEqual(condition_3.num_update_calls, 2)

            self.assertEqual(action_1.num_update_calls_enabled, 1)
            self.assertEqual(action_2.num_update_calls_enabled, 1)
            self.assertEqual(action_3.num_update_calls_enabled, 1)
            self.assertEqual(action_4.num_update_calls_enabled, 1)

        def eval3():
            self.assertEqual(condition_1.num_update_calls, 3)
            self.assertEqual(condition_2.num_update_calls, 3)
            self.assertEqual(condition_3.num_update_calls, 3)

            self.assertEqual(condition_1.true, True)
            self.assertEqual(condition_2.true, True)
            self.assertEqual(condition_3.true, True)

            self.assertEqual(action_1.num_update_calls_enabled, 2)
            self.assertEqual(action_2.num_update_calls_enabled, 2)
            self.assertEqual(action_3.num_update_calls_enabled, 1)
            self.assertEqual(action_4.num_update_calls_enabled, 1)
            return True
        
        # Step 4: Still true
        def prep4():
            period.exceed_next_time = True
            
            self.assertEqual(condition_1.num_update_calls, 3)
            self.assertEqual(condition_1.true, True)

            self.assertEqual(condition_2.num_update_calls, 3)
            self.assertEqual(condition_2.true, True)

            self.assertEqual(condition_3.num_update_calls, 3)
            self.assertEqual(condition_3.true, True)

            self.assertEqual(action_1.num_update_calls_enabled, 2)
            self.assertEqual(action_2.num_update_calls_enabled, 2)
            self.assertEqual(action_3.num_update_calls_enabled, 1)
            self.assertEqual(action_4.num_update_calls_enabled, 1)

        def eval4():
            self.assertEqual(condition_1.num_update_calls, 4)
            self.assertEqual(condition_1.true, True)
            
            self.assertEqual(condition_2.num_update_calls, 4)
            self.assertEqual(condition_2.true, True)

            self.assertEqual(condition_3.num_update_calls, 4)
            self.assertEqual(condition_3.true, True)

            self.assertEqual(action_1.num_update_calls_enabled, 3)
            self.assertEqual(action_2.num_update_calls_enabled, 3)
            self.assertEqual(action_3.num_update_calls_enabled, 1)
            self.assertEqual(action_4.num_update_calls_enabled, 1)
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

        
############################################################################################


    def test_actions_deep_conditions(self):
        switch_1 = MockSwitch()
        
        action_0 = MockAction()
        action_1 = MockAction()
        action_2 = MockAction()
        action_3 = MockAction()

        period = MockPeriodCounter()

        condition_3 = MockCondition(
            no = [
                action_3
            ]
        )

        condition_2 = MockCondition(
            yes = [
                action_2
            ],
            no = condition_3
        )

        condition_1 = MockCondition(
            yes = condition_2,
            no = [
                action_1
            ]
        )

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
                        action_0,
                        condition_1
                    ]
                }
            ],
            period_counter = period
        )

        # Build scene:
        # Step 1: Conditions all true
        def prep1():
            period.exceed_next_time = True
            
            self.assertEqual(condition_1.true, True)
            self.assertEqual(condition_1.num_update_calls, 0)

            self.assertEqual(condition_2.true, True)
            self.assertEqual(condition_2.num_update_calls, 0)
            
            self.assertEqual(condition_3.true, True)
            self.assertEqual(condition_3.num_update_calls, 0)

            self.assertEqual(action_0.num_update_calls_enabled, 0)
            self.assertEqual(action_1.num_update_calls_enabled, 0)
            self.assertEqual(action_2.num_update_calls_enabled, 0)
            self.assertEqual(action_3.num_update_calls_enabled, 0)

        def eval1():
            self.assertEqual(condition_1.true, True)

            self.assertEqual(condition_1.num_update_calls, 1)
            self.assertEqual(condition_2.num_update_calls, 1)
            self.assertEqual(condition_3.num_update_calls, 1)

            self.assertEqual(action_0.num_update_calls_enabled, 1)
            self.assertEqual(action_1.num_update_calls_enabled, 0)
            self.assertEqual(action_2.num_update_calls_enabled, 1)
            self.assertEqual(action_3.num_update_calls_enabled, 0)
            return True

        # Step 2: Conditions all false
        def prep2():
            switch_1.shall_be_pushed = True
            period.exceed_next_time = True            
            condition_1.bool_value = False
            condition_2.bool_value = False
            condition_3.bool_value = False
            
            self.assertEqual(condition_1.true, True)
            self.assertEqual(condition_1.num_update_calls, 1)

            self.assertEqual(condition_2.true, True)
            self.assertEqual(condition_2.num_update_calls, 1)
            
            self.assertEqual(condition_3.true, True)
            self.assertEqual(condition_3.num_update_calls, 1)

            self.assertEqual(action_0.num_update_calls_enabled, 1)
            self.assertEqual(action_1.num_update_calls_enabled, 0)
            self.assertEqual(action_2.num_update_calls_enabled, 1)
            self.assertEqual(action_3.num_update_calls_enabled, 0)

        def eval2():
            self.assertEqual(condition_1.true, False)
            self.assertEqual(condition_2.true, False)
            self.assertEqual(condition_2.true, False)

            self.assertEqual(condition_1.num_update_calls, 2)
            self.assertEqual(condition_2.num_update_calls, 2)
            self.assertEqual(condition_3.num_update_calls, 2)

            self.assertEqual(action_0.num_update_calls_enabled, 2)
            self.assertEqual(action_1.num_update_calls_enabled, 1)
            self.assertEqual(action_2.num_update_calls_enabled, 1)
            self.assertEqual(action_3.num_update_calls_enabled, 0)
            return True
        
        # Step 3: Condition 1 true again
        def prep3():
            period.exceed_next_time = True
            condition_1.bool_value = True

            self.assertEqual(condition_1.true, False)
            self.assertEqual(condition_1.num_update_calls, 2)

            self.assertEqual(condition_2.true, False)
            self.assertEqual(condition_2.num_update_calls, 2)

            self.assertEqual(condition_3.true, False)
            self.assertEqual(condition_3.num_update_calls, 2)

            self.assertEqual(action_0.num_update_calls_enabled, 2)
            self.assertEqual(action_1.num_update_calls_enabled, 1)
            self.assertEqual(action_2.num_update_calls_enabled, 1)
            self.assertEqual(action_3.num_update_calls_enabled, 0)

        def eval3():
            self.assertEqual(condition_1.num_update_calls, 3)
            self.assertEqual(condition_2.num_update_calls, 3)
            self.assertEqual(condition_3.num_update_calls, 3)

            self.assertEqual(condition_1.true, True)
            self.assertEqual(condition_2.true, False)
            self.assertEqual(condition_3.true, False)

            self.assertEqual(action_0.num_update_calls_enabled, 3)
            self.assertEqual(action_1.num_update_calls_enabled, 1)
            self.assertEqual(action_2.num_update_calls_enabled, 1)
            self.assertEqual(action_3.num_update_calls_enabled, 1)
            return True
        
        # Step 4: Condition 2 true again
        def prep4():
            switch_1.shall_be_pushed = False
            period.exceed_next_time = True
            condition_2.bool_value = True
            
            self.assertEqual(condition_1.num_update_calls, 3)
            self.assertEqual(condition_1.true, True)

            self.assertEqual(condition_2.num_update_calls, 3)
            self.assertEqual(condition_2.true, False)

            self.assertEqual(condition_3.num_update_calls, 3)
            self.assertEqual(condition_3.true, False)

            self.assertEqual(action_0.num_update_calls_enabled, 3)
            self.assertEqual(action_1.num_update_calls_enabled, 1)
            self.assertEqual(action_2.num_update_calls_enabled, 1)
            self.assertEqual(action_3.num_update_calls_enabled, 1)

        def eval4():
            self.assertEqual(condition_1.num_update_calls, 4)
            self.assertEqual(condition_1.true, True)
            
            self.assertEqual(condition_2.num_update_calls, 4)
            self.assertEqual(condition_2.true, True)

            self.assertEqual(condition_3.num_update_calls, 4)
            self.assertEqual(condition_3.true, False)

            self.assertEqual(action_0.num_update_calls_enabled, 4)
            self.assertEqual(action_1.num_update_calls_enabled, 1)
            self.assertEqual(action_2.num_update_calls_enabled, 2)
            self.assertEqual(action_3.num_update_calls_enabled, 1)
            return True

        # Step 5: Condition 3 true again
        def prep5():
            period.exceed_next_time = True
            condition_3.bool_value = True
            
            self.assertEqual(condition_1.num_update_calls, 4)
            self.assertEqual(condition_1.true, True)

            self.assertEqual(condition_2.num_update_calls, 4)
            self.assertEqual(condition_2.true, True)

            self.assertEqual(condition_3.num_update_calls, 4)
            self.assertEqual(condition_3.true, False)

            self.assertEqual(action_0.num_update_calls_enabled, 4)
            self.assertEqual(action_1.num_update_calls_enabled, 1)
            self.assertEqual(action_2.num_update_calls_enabled, 2)
            self.assertEqual(action_3.num_update_calls_enabled, 1)

        def eval5():
            self.assertEqual(condition_1.num_update_calls, 5)
            self.assertEqual(condition_1.true, True)
            
            self.assertEqual(condition_2.num_update_calls, 5)
            self.assertEqual(condition_2.true, True)

            self.assertEqual(condition_3.num_update_calls, 5)
            self.assertEqual(condition_3.true, True)

            self.assertEqual(action_0.num_update_calls_enabled, 5)
            self.assertEqual(action_1.num_update_calls_enabled, 1)
            self.assertEqual(action_2.num_update_calls_enabled, 3)
            self.assertEqual(action_3.num_update_calls_enabled, 1)
            return True
        
        # Step 6: Condition 2 false again
        def prep6():
            period.exceed_next_time = True
            condition_2.bool_value = False
            
            self.assertEqual(condition_1.num_update_calls, 5)
            self.assertEqual(condition_1.true, True)

            self.assertEqual(condition_2.num_update_calls, 5)
            self.assertEqual(condition_2.true, True)

            self.assertEqual(condition_3.num_update_calls, 5)
            self.assertEqual(condition_3.true, True)

            self.assertEqual(action_0.num_update_calls_enabled, 5)
            self.assertEqual(action_1.num_update_calls_enabled, 1)
            self.assertEqual(action_2.num_update_calls_enabled, 3)
            self.assertEqual(action_3.num_update_calls_enabled, 1)

        def eval6():
            self.assertEqual(condition_1.num_update_calls, 6)
            self.assertEqual(condition_1.true, True)
            
            self.assertEqual(condition_2.num_update_calls, 6)
            self.assertEqual(condition_2.true, False)

            self.assertEqual(condition_3.num_update_calls, 6)
            self.assertEqual(condition_3.true, True)

            self.assertEqual(action_0.num_update_calls_enabled, 6)
            self.assertEqual(action_1.num_update_calls_enabled, 1)
            self.assertEqual(action_2.num_update_calls_enabled, 3)
            self.assertEqual(action_3.num_update_calls_enabled, 1)
            return False

        # Build scenes hierarchy
        appl.next_step = SceneStep(
            num_pass_ticks = 10,
            prepare = prep1,
            evaluate = eval1,

            next = SceneStep(
                num_pass_ticks = 0,
                prepare = prep2,
                evaluate = eval2,
            
                next = SceneStep(
                    num_pass_ticks = 0,
                    prepare = prep3,
                    evaluate = eval3,
            
                    next = SceneStep(
                        num_pass_ticks = 1,
                        prepare = prep4,
                        evaluate = eval4,

                        next = SceneStep(
                            num_pass_ticks = 2,
                            prepare = prep5,
                            evaluate = eval5,

                            next = SceneStep(
                                num_pass_ticks = 500,
                                prepare = prep6,
                                evaluate = eval6
                            )
                        )
                    )
                )
            )
        )

        # Run process
        appl.process()


############################################################################################


    def test_actions_deep_conditions_with_hold(self):
        switch_1 = MockSwitch()
        
        action_0 = MockAction()
        action_1 = MockAction()
        action_2 = MockAction()
        action_3 = MockAction()
        action_4 = MockAction()
        action_5 = MockAction()

        period = MockPeriodCounter()
        period_hold = MockPeriodCounter()

        condition_3 = MockCondition(
            no = [
                action_3
            ]
        )

        condition_2 = MockCondition(
            yes = [
                action_2
            ],
            no = condition_3
        )

        condition_1 = MockCondition(
            yes = [
                action_5,
                HoldAction(
                    config = {
                        "actions": condition_2,
                        "actionsHold": action_4
                    },
                    period_counter_hold = period_hold
                )
            ],
            no = [
                action_1
            ]
        )

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
                        action_0,
                        condition_1
                    ]
                }
            ],
            period_counter = period
        )

        # Build scene:
        # Step 1: Conditions all true
        def prep1():
            period.exceed_next_time = True
            
            self.assertEqual(condition_1.true, True)
            self.assertEqual(condition_1.num_update_calls, 0)

            self.assertEqual(condition_2.true, True)
            self.assertEqual(condition_2.num_update_calls, 0)
            
            self.assertEqual(condition_3.true, True)
            self.assertEqual(condition_3.num_update_calls, 0)

            self.assertEqual(action_0.num_update_calls_enabled, 0)
            self.assertEqual(action_1.num_update_calls_enabled, 0)
            self.assertEqual(action_2.num_update_calls_enabled, 0)
            self.assertEqual(action_3.num_update_calls_enabled, 0)
            self.assertEqual(action_4.num_update_calls_enabled, 0)
            self.assertEqual(action_5.num_update_calls_enabled, 0)

        def eval1():
            self.assertEqual(condition_1.true, True)

            self.assertEqual(condition_1.num_update_calls, 1)
            self.assertEqual(condition_2.num_update_calls, 1)
            self.assertEqual(condition_3.num_update_calls, 1)

            self.assertEqual(action_0.num_update_calls_enabled, 1)
            self.assertEqual(action_1.num_update_calls_enabled, 0)
            self.assertEqual(action_2.num_update_calls_enabled, 1)
            self.assertEqual(action_3.num_update_calls_enabled, 0)
            self.assertEqual(action_4.num_update_calls_enabled, 1)
            self.assertEqual(action_5.num_update_calls_enabled, 1)
            return True

        # Step 2: Conditions all false
        def prep2():
            switch_1.shall_be_pushed = True
            period.exceed_next_time = True            
            condition_1.bool_value = False
            condition_2.bool_value = False
            condition_3.bool_value = False
            
            self.assertEqual(condition_1.true, True)
            self.assertEqual(condition_1.num_update_calls, 1)

            self.assertEqual(condition_2.true, True)
            self.assertEqual(condition_2.num_update_calls, 1)
            
            self.assertEqual(condition_3.true, True)
            self.assertEqual(condition_3.num_update_calls, 1)

            self.assertEqual(action_0.num_update_calls_enabled, 1)
            self.assertEqual(action_1.num_update_calls_enabled, 0)
            self.assertEqual(action_2.num_update_calls_enabled, 1)
            self.assertEqual(action_3.num_update_calls_enabled, 0)
            self.assertEqual(action_4.num_update_calls_enabled, 1)
            self.assertEqual(action_5.num_update_calls_enabled, 1)

        def eval2():
            self.assertEqual(condition_1.true, False)
            self.assertEqual(condition_2.true, False)
            self.assertEqual(condition_2.true, False)

            self.assertEqual(condition_1.num_update_calls, 2)
            self.assertEqual(condition_2.num_update_calls, 2)
            self.assertEqual(condition_3.num_update_calls, 2)

            self.assertEqual(action_0.num_update_calls_enabled, 2)
            self.assertEqual(action_1.num_update_calls_enabled, 1)
            self.assertEqual(action_2.num_update_calls_enabled, 1)
            self.assertEqual(action_3.num_update_calls_enabled, 0)
            self.assertEqual(action_4.num_update_calls_enabled, 1)
            self.assertEqual(action_5.num_update_calls_enabled, 1)
            return True
        
        # Step 3: Condition 1 true again
        def prep3():
            period.exceed_next_time = True
            condition_1.bool_value = True

            self.assertEqual(condition_1.true, False)
            self.assertEqual(condition_1.num_update_calls, 2)

            self.assertEqual(condition_2.true, False)
            self.assertEqual(condition_2.num_update_calls, 2)

            self.assertEqual(condition_3.true, False)
            self.assertEqual(condition_3.num_update_calls, 2)

            self.assertEqual(action_0.num_update_calls_enabled, 2)
            self.assertEqual(action_1.num_update_calls_enabled, 1)
            self.assertEqual(action_2.num_update_calls_enabled, 1)
            self.assertEqual(action_3.num_update_calls_enabled, 0)
            self.assertEqual(action_4.num_update_calls_enabled, 1)
            self.assertEqual(action_5.num_update_calls_enabled, 1)

        def eval3():
            self.assertEqual(condition_1.num_update_calls, 3)
            self.assertEqual(condition_2.num_update_calls, 3)
            self.assertEqual(condition_3.num_update_calls, 3)

            self.assertEqual(condition_1.true, True)
            self.assertEqual(condition_2.true, False)
            self.assertEqual(condition_3.true, False)

            self.assertEqual(action_0.num_update_calls_enabled, 3)
            self.assertEqual(action_1.num_update_calls_enabled, 1)
            self.assertEqual(action_2.num_update_calls_enabled, 1)
            self.assertEqual(action_3.num_update_calls_enabled, 1)
            self.assertEqual(action_4.num_update_calls_enabled, 2)
            self.assertEqual(action_5.num_update_calls_enabled, 2)
            return True
        
        # Step 4: Condition 2 true again
        def prep4():
            switch_1.shall_be_pushed = False
            period.exceed_next_time = True
            condition_2.bool_value = True
            
            self.assertEqual(condition_1.num_update_calls, 3)
            self.assertEqual(condition_1.true, True)

            self.assertEqual(condition_2.num_update_calls, 3)
            self.assertEqual(condition_2.true, False)

            self.assertEqual(condition_3.num_update_calls, 3)
            self.assertEqual(condition_3.true, False)

            self.assertEqual(action_0.num_update_calls_enabled, 3)
            self.assertEqual(action_1.num_update_calls_enabled, 1)
            self.assertEqual(action_2.num_update_calls_enabled, 1)
            self.assertEqual(action_3.num_update_calls_enabled, 1)
            self.assertEqual(action_4.num_update_calls_enabled, 2)
            self.assertEqual(action_5.num_update_calls_enabled, 2)

        def eval4():
            self.assertEqual(condition_1.num_update_calls, 4)
            self.assertEqual(condition_1.true, True)
            
            self.assertEqual(condition_2.num_update_calls, 4)
            self.assertEqual(condition_2.true, True)

            self.assertEqual(condition_3.num_update_calls, 4)
            self.assertEqual(condition_3.true, False)

            self.assertEqual(action_0.num_update_calls_enabled, 4)
            self.assertEqual(action_1.num_update_calls_enabled, 1)
            self.assertEqual(action_2.num_update_calls_enabled, 2)
            self.assertEqual(action_3.num_update_calls_enabled, 1)
            self.assertEqual(action_4.num_update_calls_enabled, 3)
            self.assertEqual(action_5.num_update_calls_enabled, 3)
            return True

        # Step 5: Condition 3 true again
        def prep5():
            period.exceed_next_time = True
            condition_3.bool_value = True
            
            self.assertEqual(condition_1.num_update_calls, 4)
            self.assertEqual(condition_1.true, True)

            self.assertEqual(condition_2.num_update_calls, 4)
            self.assertEqual(condition_2.true, True)

            self.assertEqual(condition_3.num_update_calls, 4)
            self.assertEqual(condition_3.true, False)

            self.assertEqual(action_0.num_update_calls_enabled, 4)
            self.assertEqual(action_1.num_update_calls_enabled, 1)
            self.assertEqual(action_2.num_update_calls_enabled, 2)
            self.assertEqual(action_3.num_update_calls_enabled, 1)
            self.assertEqual(action_4.num_update_calls_enabled, 3)
            self.assertEqual(action_5.num_update_calls_enabled, 3)

        def eval5():
            self.assertEqual(condition_1.num_update_calls, 5)
            self.assertEqual(condition_1.true, True)
            
            self.assertEqual(condition_2.num_update_calls, 5)
            self.assertEqual(condition_2.true, True)

            self.assertEqual(condition_3.num_update_calls, 5)
            self.assertEqual(condition_3.true, True)

            self.assertEqual(action_0.num_update_calls_enabled, 5)
            self.assertEqual(action_1.num_update_calls_enabled, 1)
            self.assertEqual(action_2.num_update_calls_enabled, 3)
            self.assertEqual(action_3.num_update_calls_enabled, 1)
            self.assertEqual(action_4.num_update_calls_enabled, 4)
            self.assertEqual(action_5.num_update_calls_enabled, 4)
            return True
        
        # Step 6: Condition 2 false again
        def prep6():
            period.exceed_next_time = True
            condition_2.bool_value = False
            
            self.assertEqual(condition_1.num_update_calls, 5)
            self.assertEqual(condition_1.true, True)

            self.assertEqual(condition_2.num_update_calls, 5)
            self.assertEqual(condition_2.true, True)

            self.assertEqual(condition_3.num_update_calls, 5)
            self.assertEqual(condition_3.true, True)

            self.assertEqual(action_0.num_update_calls_enabled, 5)
            self.assertEqual(action_1.num_update_calls_enabled, 1)
            self.assertEqual(action_2.num_update_calls_enabled, 3)
            self.assertEqual(action_3.num_update_calls_enabled, 1)
            self.assertEqual(action_4.num_update_calls_enabled, 4)
            self.assertEqual(action_5.num_update_calls_enabled, 4)

        def eval6():
            self.assertEqual(condition_1.num_update_calls, 6)
            self.assertEqual(condition_1.true, True)
            
            self.assertEqual(condition_2.num_update_calls, 6)
            self.assertEqual(condition_2.true, False)

            self.assertEqual(condition_3.num_update_calls, 6)
            self.assertEqual(condition_3.true, True)

            self.assertEqual(action_0.num_update_calls_enabled, 6)
            self.assertEqual(action_1.num_update_calls_enabled, 1)
            self.assertEqual(action_2.num_update_calls_enabled, 3)
            self.assertEqual(action_3.num_update_calls_enabled, 1)
            self.assertEqual(action_4.num_update_calls_enabled, 5)
            self.assertEqual(action_5.num_update_calls_enabled, 5)
            return False

        # Build scenes hierarchy
        appl.next_step = SceneStep(
            num_pass_ticks = 10,
            prepare = prep1,
            evaluate = eval1,

            next = SceneStep(
                num_pass_ticks = 0,
                prepare = prep2,
                evaluate = eval2,
            
                next = SceneStep(
                    num_pass_ticks = 0,
                    prepare = prep3,
                    evaluate = eval3,
            
                    next = SceneStep(
                        num_pass_ticks = 1,
                        prepare = prep4,
                        evaluate = eval4,

                        next = SceneStep(
                            num_pass_ticks = 2,
                            prepare = prep5,
                            evaluate = eval5,

                            next = SceneStep(
                                num_pass_ticks = 500,
                                prepare = prep6,
                                evaluate = eval6
                            )
                        )
                    )
                )
            )
        )

        # Run process
        appl.process()


############################################################################################


    def test_condition_invalid_subject(self):
        with self.assertRaises(Exception):            
            ConditionTree(
                [
                    MockCondition(
                        yes = "Foo",
                        no = MockCondition(
                            yes = "Bar",
                            no = "Fdd"
                        )
                    ),
                    None
                ],
                allow_lists = False
            )

############################################################################################


    def test_condition_replacer(self):
        repl = MockConditionReplacer()

        tree = ConditionTree(
            [
                MockCondition(
                    yes = "Foo",
                    no = MockCondition(
                        yes = "Bar",
                        no = "Fdd"
                    )
                ),
                None
            ],
            replacer = repl
        )

        rep = self._get_tree_repr(tree._tree)

        self.assertEqual("Foo (replaced)" in rep, True)
        self.assertEqual("Bar (replaced)" in rep, True)
        self.assertEqual("Fdd (replaced)" in rep, True)
        self.assertEqual("MockCondition" in rep, True)


    # Returns a representation of the passed tree
    def _get_tree_repr(self, subject, indent = 0):
        indent_str = "".join([" " for i in range(indent)])
        
        if subject == None:
            return indent_str + repr(None) + "\n"
        
        elif isinstance(subject, list):
            ret = indent_str + "[\n"
    
            for entry in subject:
                ret += self._get_tree_repr(entry, indent + 2)
    
            return ret + indent_str + "]\n"
    
        elif isinstance(subject, Condition):
            indent_str_p2 = "".join([" " for i in range(indent + 2)])
    
            ret = indent_str + subject.__class__.__name__ + "(\n"
           
            ret += indent_str_p2 + "yes: \n"
            ret +=  self._get_tree_repr(subject.yes, indent + 4)
    
            ret += indent_str_p2 + "no: \n"
            ret += self._get_tree_repr(subject.no, indent + 4)
    
            return ret + indent_str + ")\n"
        
        else:
            return indent_str + repr(subject) + "\n"


    def test_condition_repr(self):
        tree = ConditionTree(
            [
                MockCondition(
                    yes = "Foo",
                    no = MockCondition(
                        yes = "Bar",
                        no = "Fdd"
                    )
                ),
                None
            ]
        )

        rep = self._get_tree_repr(tree._tree)

        self.assertEqual("Foo" in rep, True)
        self.assertEqual("Bar" in rep, True)
        self.assertEqual("Fdd" in rep, True)
        self.assertEqual("MockCondition" in rep, True)


############################################################################################


    def test_condition_init_no_updater(self):
        tree = ConditionTree(None)

        with self.assertRaises(Exception):           
            tree.init({})


############################################################################################


    def test_condition_properties_list(self):
        condition_2 = MockCondition(
            yes = ["Bar", "Bart"],
            no = "Fdd"
        )

        condition_1 = MockCondition(
            yes = "Foo",
            no = [
                condition_2,
                "Fart"
            ]
        )

        tree = ConditionTree(
            [
                condition_1,
                None
            ]
        )

        self.assertEqual(len(tree.conditions), 2)

        self.assertEqual(tree.values, ["Foo"])

        condition_1.true = False
        self.assertEqual(len(tree.values), 3)
        self.assertEqual("Fart" in tree.values, True)
        self.assertEqual("Bar" in tree.values, True)
        self.assertEqual("Bart" in tree.values, True)

        condition_2.true = False
        self.assertEqual(len(tree.values), 2)
        self.assertEqual("Fart" in tree.values, True)
        self.assertEqual("Fdd" in tree.values, True)

        with self.assertRaises(Exception): 
            tree.value


############################################################################################


    def test_condition_properties_nolist(self):
        condition_2 = MockCondition(
            yes = "Bar",
            no = "Fdd"
        )

        condition_1 = MockCondition(
            yes = "Foo",
            no = condition_2
        )

        tree = ConditionTree(
            condition_1,
            allow_lists = False
        )

        self.assertEqual(len(tree.conditions), 2)

        self.assertEqual(tree.value, "Foo")

        condition_1.true = False
        self.assertEqual(tree.value, "Bar")

        condition_2.true = False
        self.assertEqual(tree.value, "Fdd")

        with self.assertRaises(Exception): 
            tree.values

