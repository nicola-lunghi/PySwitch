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
    from adafruit_midi.system_exclusive import SystemExclusive

    from lib.pyswitch.controller.actions.actions import ParameterAction, PushButtonModes
    from lib.pyswitch.controller.Client import ClientParameterMapping
    from lib.pyswitch.misc import Tools



class TestActionParameter(unittest.TestCase):

    def test_set_parameter(self):
        switch_1 = MockSwitch()
        
        mapping_1 = ClientParameterMapping(
            name = "", 
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x01, 0x02, 0x03, 0x04]
            )
        )

        action_1 = ParameterAction({
            "mode": PushButtonModes.MOMENTARY,
            "mapping": mapping_1,
            "valueEnabled": 10,
            "valueDisabled": 3
        })
        
        vp = MockValueProvider()

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            value_provider = vp,
            switches = [
                {
                    "assignment": {
                        "model": switch_1
                    },
                    "actions": [
                        action_1                        
                    ]
                }
            ]
        )

        # Build scene:
        # Step 1: Enable
        def prep1():
            switch_1.shall_be_pushed = True

        def eval1():
            self.assertEqual(len(vp.set_value_calls), 1)
            self.assertDictEqual(vp.set_value_calls[0], {
                "mapping": mapping_1,
                "value": 10
            })

            self.assertEqual(len(appl._midi.messages_sent), 1)
            self.assertTrue(Tools.compare_midi_messages(appl._midi.messages_sent[0], mapping_1.set))
            return True        
        
        # Step 2: Disable
        def prep2():
            switch_1.shall_be_pushed = False

        def eval2():
            self.assertEqual(len(vp.set_value_calls), 2)
            self.assertDictEqual(vp.set_value_calls[1], {
                "mapping": mapping_1,
                "value": 3
            })

            self.assertEqual(len(appl._midi.messages_sent), 2)
            self.assertTrue(Tools.compare_midi_messages(appl._midi.messages_sent[1], mapping_1.set))
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


###############################################################################################


    def test_request_parameter(self):
        switch_1 = MockSwitch()
        
        mapping_1 = ClientParameterMapping(
            name = "", 
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0x09]
            )
        )

        action_1 = ParameterAction({
            "mapping": mapping_1
        })
        
        period = MockPeriodCounter()

        vp = MockValueProvider()

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            value_provider = vp,
            switches = [
                {
                    "assignment": {
                        "model": switch_1
                    },
                    "actions": [
                        action_1                        
                    ]
                }
            ],
            period_counter = period
        )

        answer_msg_1 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0x09, 0x44]
        )

        answer_msg_2 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0x07, 0x45]
        )

        # Build scene:
        # Send update request
        def prep1():
            period.exceed_next_time = True

        def eval1():
            self.assertEqual(len(appl._midi.messages_sent), 1)
            self.assertEqual(appl._midi.messages_sent[0], mapping_1.request)
            return True

        # Step without update
        def eval2():
            self.assertEqual(len(appl._midi.messages_sent), 1)
            return True

        # Receive value 
        def prep3():
            period.exceed_next_time = True
            appl._midi.next_receive_messages = [
                answer_msg_1,
                answer_msg_2
            ]
            vp.outputs_parse = [
                {
                    "result": True,
                    "value": 1
                },
                {
                    "result": False
                }
            ]

        def eval3():
            self.assertEqual(len(vp.parse_calls), 1)

            self.assertEqual(vp.parse_calls[0]["mapping"], mapping_1)
            self.assertTrue(Tools.compare_midi_messages(vp.parse_calls[0]["message"], answer_msg_1))

            self.assertEqual(mapping_1.value, 1)

            return True
        
        # Receive value 
        def prep4():
            period.exceed_next_time = True
            appl._midi.next_receive_messages = [
                answer_msg_1
            ]
            vp.outputs_parse = [
                {
                    "result": True,
                    "value": 0
                }
            ]

        def eval4():
            self.assertEqual(len(vp.parse_calls), 2)

            self.assertEqual(vp.parse_calls[1]["mapping"], mapping_1)
            self.assertTrue(Tools.compare_midi_messages(vp.parse_calls[1]["message"], answer_msg_1))

            self.assertEqual(mapping_1.value, 0)

            return False

        # Build scenes hierarchy
        appl.next_step = SceneStep(
            num_pass_ticks = 5,
            prepare = prep1,
            evaluate = eval1,

            next = SceneStep(
                num_pass_ticks = 5,
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

