import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

# Import subject under test
with patch.dict(sys.modules, {
    "micropython": MockMicropython,
    "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
    "usb_midi": MockUsbMidi(),
    "adafruit_midi": MockAdafruitMIDI(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "adafruit_midi.program_change": MockAdafruitMIDIProgramChange(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "gc": MockGC()
}):
    from adafruit_midi.system_exclusive import SystemExclusive

    from lib.pyswitch.controller.actions.actions import PushButtonAction
    from lib.pyswitch.controller.actions.callbacks import BinaryParameterCallback
    from lib.pyswitch.controller.Client import BidirectionalClient
    #from lib.pyswitch.misc import compare_midi_messages

    from.mocks_appl import *
    

class TestBidirectionalClient(unittest.TestCase):

    def test_register(self):
        midi = MockMidiController()

        mapping_1 = MockParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x01, 0x02, 0x03, 0x04]
            ),
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0x09]
            )
        )

        mapping_2 = MockParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x21],
                data = [0x01, 0x02, 0x03, 0x04]
            ),
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x24],
                data = [0x00, 0x00, 0x09]
            )
        )

        protocol = MockBidirectionalProtocol()
        protocol.outputs_is_bidirectional = [
            {
                "mapping": mapping_1,
                "result": True
            }
        ]

        client = BidirectionalClient(
            midi = midi,
            config = {},            
            protocol = protocol
        )
        
        listener = MockClientRequestListener()
        
        client.register(mapping_1, listener)
        req = client.requests[0]
        self.assertEqual(len(client.requests), 1)
        self.assertEqual(req.mapping, mapping_1)
        self.assertIn(listener, req.listeners)
        self.assertEqual(len(midi.messages_sent), 0)

        client.register(mapping_2, listener)
        self.assertEqual(len(client.requests), 1)
        
        # Update
        self.assertEqual(protocol.num_update_calls, 0)
        client.update()
        self.assertEqual(protocol.num_update_calls, 1)


#############################################################################################


    def test_notify_connection_lost(self):
        midi = MockMidiController()

        mapping_1 = MockParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x01, 0x02, 0x03, 0x04]
            ),
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0x09]
            )
        )

        mapping_2 = MockParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x21],
                data = [0x01, 0x02, 0x03, 0x34]
            ),
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x29]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x24],
                data = [0x00, 0x00, 0x19]
            )
        )

        protocol = MockBidirectionalProtocol()
        protocol.outputs_is_bidirectional = [
            {
                "mapping": mapping_1,
                "result": True
            }
        ]

        client = BidirectionalClient(
            midi = midi,
            config = {},            
            protocol = protocol
        )
        
        listener = MockClientRequestListener()
        
        client.register(mapping_1, listener)
        client.register(mapping_2, listener)

        client.notify_connection_lost()
        self.assertEqual(listener.request_terminated_calls, [mapping_1])

        client.notify_connection_lost()
        self.assertEqual(listener.request_terminated_calls, [mapping_1, mapping_1])


#############################################################################################


    def test_all(self):
        self._test_all(True)
        self._test_all(False)  # No value feedback


    def _test_all(self, do_feedback):
        switch_1 = MockSwitch()

        mapping_1 = MockParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x01, 0x02, 0x03, 0x04]
            ),
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0x09]
            )
        )

        mapping_2 = MockParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x11, 0x20],
                data = [0x01, 0x02, 0x03, 0x14]
            ),
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x20, 0x20],
                data = [0x05, 0x07, 0x02]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x02, 0x10, 0x20],
                data = [0x00, 0x00, 0x29]
            )
        )

        action_1 = PushButtonAction({
            "callback": BinaryParameterCallback(
                mapping = mapping_1,
                comparison_mode = BinaryParameterCallback.GREATER_EQUAL,
                color = (10, 50, 100)
            ),
            "mode": PushButtonAction.LATCH
        })

        action_2 = PushButtonAction({
            "callback": BinaryParameterCallback(
                mapping = mapping_2,
                comparison_mode = BinaryParameterCallback.GREATER_EQUAL,
                color = (10, 50, 100)
            ),
            "mode": PushButtonAction.LATCH
        })
        
        period = MockPeriodCounter()

        protocol = MockBidirectionalProtocol()
        protocol.outputs_is_bidirectional = [
            {
                "mapping": mapping_1,
                "result": True
            }
        ]
        
        protocol.outputs_feedback_value = [
            {
                "mapping": mapping_1,
                "result": do_feedback
            }
        ]

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            protocol = protocol,
            midi = MockMidiController(),
            switches = [
                {
                    "assignment": {
                        "model": switch_1
                    },
                    "actions": [
                        action_1,
                        action_2                     
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
            manufacturer_id = [0x00, 0x12, 0x20],
            data = [0x00, 0x01, 0x09, 0x44]
        )

        # Build scene:
        # Send update request
        def prep1():
            period.exceed_next_time = True

        def eval1():
            self.assertEqual(len(appl._midi.messages_sent), 1)
            self.assertEqual(appl._midi.messages_sent[0], mapping_2.request)
            
            return True

        # Receive type
        def prep2():
            appl._midi.next_receive_messages = [
                answer_msg_2
            ]
            mapping_2.outputs_parse = [
                {
                    "message": answer_msg_2,
                    "value": 1
                }
            ]

        def eval2():
            self.assertEqual(len(appl._midi.next_receive_messages), 0)

            self.assertEqual(len(appl._midi.messages_sent), 1)

            self.assertEqual(mapping_2.value, 1)
            
            self.assertEqual(action_1.state, False)
            self.assertEqual(action_2.state, True)
            
            self.assertNotIn(answer_msg_2, protocol.receive_calls)

            return True

        # Receive status (which is bidirectional)
        def prep3():
            appl._midi.next_receive_messages = [
                answer_msg_1
            ]
            mapping_1.outputs_parse = [
                {
                    "message": answer_msg_1,
                    "value": 1
                }
            ]

        def eval3():
            self.assertEqual(len(appl._midi.next_receive_messages), 0)

            self.assertEqual(len(appl._midi.messages_sent), 1)
            
            self.assertEqual(appl.client.requests[0].mapping.value, 1)

            self.assertNotIn(answer_msg_1, protocol.receive_calls)

            self.assertEqual(action_1.state, True)
            self.assertEqual(action_2.state, True)

            return True
        
        # Set status (check if feedback is working)
        def prep4():
            switch_1.shall_be_pushed = True

        def eval4():
            self.assertEqual(len(appl._midi.messages_sent), 4)
            self.assertIn(mapping_1.set, appl._midi.messages_sent)
            self.assertIn(mapping_2.set, appl._midi.messages_sent)
            self.assertIn(mapping_2.request, appl._midi.messages_sent)
            self.assertEqual(action_1.state, False)

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