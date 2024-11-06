import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

with patch.dict(sys.modules, {
    "usb_midi": MockUsbMidi(),
    "adafruit_midi": MockAdafruitMIDI(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "gc": MockGC()
}):
    from .mocks_appl import *

    from adafruit_midi.system_exclusive import SystemExclusive

    from lib.pyswitch.controller.ConditionTree import ParameterCondition, ParameterConditionModes
    from lib.pyswitch.controller.Client import ClientParameterMapping
    from lib.pyswitch.misc import Tools


class TestConditionParameter(unittest.TestCase):

    def test_functionality(self):
        self._test_functionality(
            mode = ParameterConditionModes.MODE_EQUAL,
            ref_value = 2.2,
            
            answer_value_1 = 2.2,
            expect_1 = True,
            
            answer_value_2 = 2.1,
            expect_2 = False,
            
            answer_value_3 = 2.3,
            expect_3 = False
        )

        self._test_functionality(
            mode = ParameterConditionModes.MODE_GREATER,
            ref_value = 2.2,
            
            answer_value_1 = 2.2,
            expect_1 = False,
            
            answer_value_2 = 2.1,
            expect_2 = False,
            
            answer_value_3 = 2.3,
            expect_3 = True
        )

        self._test_functionality(
            mode = ParameterConditionModes.MODE_GREATER_EQUAL,
            ref_value = 2.2,
            
            answer_value_1 = 2.2,
            expect_1 = True,
            
            answer_value_2 = 1,
            expect_2 = False,
            
            answer_value_3 = 1,
            expect_3 = False
        )

        self._test_functionality(
            mode = ParameterConditionModes.MODE_GREATER_EQUAL,
            ref_value = 2.2,
            
            answer_value_1 = 2.2,
            expect_1 = True,
            
            answer_value_2 = 1,
            expect_2 = False,
            
            answer_value_3 = 2.3,
            expect_3 = True
        )

        self._test_functionality(
            mode = ParameterConditionModes.MODE_LESS,
            ref_value = 2.2,
            
            answer_value_1 = 2.2,
            expect_1 = False,
            
            answer_value_2 = 2.1,
            expect_2 = True,
            
            answer_value_3 = 2.3,
            expect_3 = False
        )

        self._test_functionality(
            mode = ParameterConditionModes.MODE_LESS_EQUAL,
            ref_value = 2.2,
            
            answer_value_1 = 2.2,
            expect_1 = True,
            
            answer_value_2 = 2.1,
            expect_2 = True,
            
            answer_value_3 = 2.3,
            expect_3 = False
        )

        self._test_functionality(
            mode = ParameterConditionModes.MODE_IN_RANGE,
            ref_value = [2.2, 4.5],
            
            answer_value_1 = 2.2,
            expect_1 = True,
            
            answer_value_2 = 2.1,
            expect_2 = False,
            
            answer_value_3 = 2.3,
            expect_3 = True
        )

        self._test_functionality(
            mode = ParameterConditionModes.MODE_IN_RANGE,
            ref_value = [2.2, 4.5],
            
            answer_value_1 = 4,
            expect_1 = True,
            
            answer_value_2 = 4.5,
            expect_2 = True,
            
            answer_value_3 =4.6,
            expect_3 = False
        )

        self._test_functionality(
            mode = ParameterConditionModes.MODE_NOT_IN_RANGE,
            ref_value = [2.2, 4.5],
            
            answer_value_1 = 2.2,
            expect_1 = False,
            
            answer_value_2 = 2.1,
            expect_2 = True,
            
            answer_value_3 = 2.3,
            expect_3 = False
        )

        self._test_functionality(
            mode = ParameterConditionModes.MODE_NOT_IN_RANGE,
            ref_value = [2.2, 4.5],
            
            answer_value_1 = 4,
            expect_1 = False,
            
            answer_value_2 = 4.5,
            expect_2 = False,
            
            answer_value_3 =4.6,
            expect_3 = True
        )

        self._test_functionality(
            mode = ParameterConditionModes.MODE_STRING_CONTAINS,
            ref_value = "foo",
            
            answer_value_1 = "bar",
            expect_1 = False,
            
            answer_value_2 = "foobar",
            expect_2 = True,
            
            answer_value_3 = "fobaro",
            expect_3 = False
        )

        self._test_functionality(
            mode = ParameterConditionModes.MODE_STRING_NOT_CONTAINS,
            ref_value = "foo",
            
            answer_value_1 = "bar",
            expect_1 = True,
            
            answer_value_2 = "foobar",
            expect_2 = False,
            
            answer_value_3 = "fobaro",
            expect_3 = True
        )

        self._test_functionality(
            mode = ParameterConditionModes.MODE_STRING_STARTS_WITH,
            ref_value = "foo",
            
            answer_value_1 = "foo",
            expect_1 = True,
            
            answer_value_2 = "foobar",
            expect_2 = True,
            
            answer_value_3 = "barfoo",
            expect_3 = False
        )

        self._test_functionality(
            mode = ParameterConditionModes.MODE_STRING_STARTS_WITH,
            ref_value = "foo",
            
            answer_value_1 = "not",
            expect_1 = False,
            
            answer_value_2 = "barfoobar",
            expect_2 = False,
            
            answer_value_3 = "",
            expect_3 = False
        )

        self._test_functionality(
            mode = ParameterConditionModes.MODE_STRING_ENDS_WITH,
            ref_value = "foo",
            
            answer_value_1 = "foo",
            expect_1 = True,
            
            answer_value_2 = "foobar",
            expect_2 = False,
            
            answer_value_3 = "barfoo",
            expect_3 = True
        )

        self._test_functionality(
            mode = ParameterConditionModes.MODE_STRING_ENDS_WITH,
            ref_value = "foo",
            
            answer_value_1 = "not",
            expect_1 = False,
            
            answer_value_2 = "barfoobar",
            expect_2 = False,
            
            answer_value_3 = "",
            expect_3 = False
        )

        with self.assertRaises(Exception): 
            self._test_functionality(
                mode = -99999,
                ref_value = "foo",
                
                answer_value_1 = "not",
                expect_1 = False,
                
                answer_value_2 = "barfoobar",
                expect_2 = False,
                
                answer_value_3 = "",
                expect_3 = False
            )


    def _test_functionality(self, mode, ref_value, answer_value_1, expect_1, answer_value_2, expect_2, answer_value_3, expect_3):
        switch_1 = MockSwitch()
        action_1 = MockAction()
        action_2 = MockAction()
        period = MockPeriodCounter()

        mapping_1 = ClientParameterMapping(
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x01, 0x02, 0x03, 0x04]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0x09, 0x00]
            )
        )

        condition_1 = ParameterCondition(
            mapping = mapping_1,
            mode = mode,
            ref_value = ref_value,
            yes = [
                action_1
            ],
            no = [
                action_2
            ]
        )

        vp = MockValueProvider()

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            communication = {
                "valueProvider": vp
            },
            midi = MockMidiController(),
            switches = [
                {
                    "assignment": {
                        "model": switch_1
                    },
                    "actions": condition_1
                }
            ],
            period_counter = period
        )

        answer_msg_1 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0x09, 0x44]
        )

        # Build scene:
        # Step 1
        def prep1():
            period.exceed_next_time = True
            
        def eval1():
            self.assertEqual(len(appl._midi.messages_sent), 1)
            self.assertTrue(Tools.compare_midi_messages(appl._midi.messages_sent[0], mapping_1.request))

            return True

        # Step 2
        def prep2():
            period.exceed_next_time = True

            appl._midi.next_receive_messages = [
                answer_msg_1
            ]
            vp.outputs_parse = [
                {
                    "mapping": mapping_1,
                    "result": True,
                    "value": answer_value_1
                }
            ]   

        def eval2():
            self.assertEqual(condition_1.true, expect_1)

            self.assertEqual(action_1.enabled, expect_1)
            self.assertNotEqual(action_2.enabled, expect_1)

            return True
        
        # Step 3
        def prep3():
            period.exceed_next_time = True

            appl._midi.next_receive_messages = [
                answer_msg_1
            ]
            vp.outputs_parse = [
                {
                    "mapping": mapping_1,
                    "result": True,
                    "value": answer_value_2
                }
            ]   

        def eval3():
            self.assertEqual(len(appl._midi.messages_sent), 2)
            self.assertTrue(Tools.compare_midi_messages(appl._midi.messages_sent[1], mapping_1.request))

            self.assertEqual(condition_1.true, expect_2)

            self.assertEqual(action_1.enabled, expect_2)
            self.assertNotEqual(action_2.enabled, expect_2)

            return True
        
        # Step 4
        def prep4():
            period.exceed_next_time = True

            appl._midi.next_receive_messages = [
                answer_msg_1
            ]
            vp.outputs_parse = [
                {
                    "mapping": mapping_1,
                    "result": True,
                    "value": answer_value_3
                }
            ]   

        def eval4():
            self.assertEqual(condition_1.true, expect_3)

            self.assertEqual(action_1.enabled, expect_3)
            self.assertNotEqual(action_2.enabled, expect_3)

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


    def test_request_timeout(self):
        switch_1 = MockSwitch()
        action_1 = MockAction()
        action_2 = MockAction()
        period = MockPeriodCounter()

        mapping_1 = ClientParameterMapping(
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x01, 0x02, 0x03, 0x04]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0x09, 0x00]
            )
        )

        condition_1 = ParameterCondition(
            mapping = mapping_1,
            mode = ParameterConditionModes.MODE_GREATER_EQUAL,
            ref_value = 2.2,
            yes = [
                action_1
            ],
            no = [
                action_2
            ]
        )
        condition_1.true = False

        vp = MockValueProvider()

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            communication = {
                "valueProvider": vp
            },
            midi = MockMidiController(),
            switches = [
                {
                    "assignment": {
                        "model": switch_1
                    },
                    "actions": condition_1
                }
            ],
            period_counter = period
        )

        wa = []

        # Build scene:
        # Step 1
        def prep1():
            period.exceed_next_time = True
            
        def eval1():
            self.assertEqual(len(appl._midi.messages_sent), 1)
            self.assertTrue(Tools.compare_midi_messages(appl._midi.messages_sent[0], mapping_1.request))

            return True

        # Step 2
        def prep2():
            self.assertEqual(condition_1.true, False)

            period.exceed_next_time = True

            appl.client._cleanup_terminated_period = MockPeriodCounter()
            appl.client._cleanup_terminated_period.exceed_next_time = True

            appl.client._requests[0].lifetime = MockPeriodCounter()
            appl.client._requests[0].lifetime.exceed_next_time = True
            wa.append(appl.client._requests[0])
            
        def eval2():
            self.assertEqual(len(appl.client._requests), 0)
            self.assertEqual(wa[0].finished, True)

            self.assertEqual(condition_1.true, True)

            return False
        

        # Build scenes hierarchy
        appl.next_step = SceneStep(
            num_pass_ticks = 5,
            prepare = prep1,
            evaluate = eval1,

            next = SceneStep(
                num_pass_ticks = 5,
                prepare = prep2,
                evaluate = eval2
            )
        )

        # Run process
        appl.process()

        
############################################################################################


    def test_invalid_calls(self):
        switch_1 = MockSwitch()
        action_1 = MockAction()
        action_2 = MockAction()
        period = MockPeriodCounter()

        mapping_1 = ClientParameterMapping(
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x01, 0x02, 0x03, 0x04]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0x09, 0x00]
            )
        )

        condition_1 = ParameterCondition(
            mapping = mapping_1,
            mode = ParameterConditionModes.MODE_GREATER_EQUAL,
            ref_value = 2.2,
            yes = [
                action_1
            ],
            no = [
                action_2
            ]
        )

        with self.assertRaises(Exception):
            condition_1.update()

        vp = MockValueProvider()

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            communication = {
                "valueProvider": vp
            },
            midi = MockMidiController(),
            switches = [
                {
                    "assignment": {
                        "model": switch_1
                    },
                    "actions": condition_1
                }
            ],
            period_counter = period
        )

