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
    from adafruit_midi.system_exclusive import SystemExclusive
    from adafruit_midi.control_change import ControlChange
    from lib.pyswitch.controller.Client import Client, ClientParameterMapping, ClientRequest

    from.mocks_appl import *


class MockClient:
    def __init__(self):
        self.debug = False


class TestClient(unittest.TestCase):

    def test_set(self):
        midi = MockAdafruitMIDI.MIDI()
        vp = MockValueProvider()

        client = Client(
            midi = midi,
            config = {},
            value_provider = vp
        )

        mapping_1 = ClientParameterMapping(
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

        client.set(mapping_1, 33)

        self.assertEqual(len(midi.messages_sent), 1)
        self.assertEqual(midi.messages_sent[0], mapping_1.set)
        self.assertEqual(vp.set_value_calls, [{
            "mapping": mapping_1,
            "value": 33
        }])


##############################################################################################


    def test_set_not_settable(self):        
        midi = MockAdafruitMIDI.MIDI()
        vp = MockValueProvider()

        client = Client(
            midi = midi,
            config = {},
            value_provider = vp
        )

        mapping_1 = ClientParameterMapping(
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0x09]
            )
        )

        with self.assertRaises(Exception):           
            client.set(mapping_1, 33)

        
##############################################################################################


    def test_request(self):        
        midi = MockAdafruitMIDI.MIDI()
        vp = MockValueProvider()

        client = Client(
            midi = midi,
            config = {},
            value_provider = vp
        )

        mapping_1 = ClientParameterMapping(
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0x09]
            )
        )

        listener = MockClientRequestListener()

        client.request(mapping_1, listener)

        self.assertEqual(len(midi.messages_sent), 1)
        self.assertEqual(midi.messages_sent[0], mapping_1.request)
        
        # Receive None
        client.receive(None)
        self.assertEqual(listener.parameter_changed_calls, [])

        # Receive ControlChange
        client.receive(ControlChange(3, 4))
        self.assertEqual(listener.parameter_changed_calls, [])

        # Receive wrong message
        answer_msg = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0x07, 0x45]
        )

        vp.outputs_parse = [
            {
                "mapping": mapping_1,
                "result": False
                #"value": 0
            }
        ]

        client.receive(answer_msg)
        self.assertEqual(listener.parameter_changed_calls, [])

        # Receive correct message
        req = client.requests[0]
        answer_msg = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0x07, 0x45]
        )

        vp.outputs_parse = [
            {
                "mapping": mapping_1,
                "result": True,
                "value": 34
            }
        ]

        client.receive(answer_msg)
        self.assertEqual(listener.parameter_changed_calls, [mapping_1])
        self.assertEqual(mapping_1.value, 34)
        self.assertEqual(req.finished, True)
        self.assertEqual(client.requests, [])


##############################################################################################


    def test_request_endless(self):        
        midi = MockAdafruitMIDI.MIDI()
        vp = MockValueProvider()

        client = Client(
            midi = midi,
            config = {
                "maxRequestLifetimeMillis": 0
            },
            value_provider = vp
        )

        mapping_1 = ClientParameterMapping(
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0x09]
            )
        )

        listener = MockClientRequestListener()

        client.register(mapping_1, listener)

        answer_msg = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0x07, 0x45]
        )
        
        vp.outputs_parse = [
            {
                "mapping": mapping_1,
                "result": True,
                "value": 34
            }
        ]

        req = client.requests[0]

        client.receive(answer_msg)
        self.assertEqual(listener.parameter_changed_calls, [mapping_1])        
        
        self.assertEqual(mapping_1.value, 34)
        self.assertEqual(req.finished, False)
        self.assertTrue(req in client.requests)


##############################################################################################


    def test_request_terminate(self):        
        midi = MockAdafruitMIDI.MIDI()
        vp = MockValueProvider()

        client = Client(
            midi = midi,
            config = {},
            value_provider = vp
        )

        mapping_1 = ClientParameterMapping(
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0x09]
            )
        )

        listener = MockClientRequestListener()

        client.request(mapping_1, listener)

        self.assertEqual(len(midi.messages_sent), 1)
        self.assertEqual(midi.messages_sent[0], mapping_1.request)
        
        req = client.requests[0]        
        req.terminate()
        self.assertEqual(req.finished, True)

        answer_msg = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0x07, 0x45]
        )

        vp.outputs_parse = [
            {
                "mapping": mapping_1,
                "result": True,
                "value": 34
            }
        ]

        client.receive(answer_msg)
        self.assertEqual(listener.parameter_changed_calls, [])
        self.assertEqual(mapping_1.value, None)
        
        self.assertEqual(client.requests, [])


##############################################################################################


    def test_mapping_eq_response(self):
        mapping_1 = ClientParameterMapping(
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0x09]
            )
        )

        mapping_2 = ClientParameterMapping(
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x10]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0x09]
            )
        )

        self.assertFalse(mapping_1 == None)
        self.assertFalse(None == mapping_2)

        self.assertTrue(mapping_1 == mapping_2)

        mapping_2.response.data[1] = 0x01
        self.assertTrue(mapping_1 != mapping_2)

        mapping_2.response.data[1] = 0x00
        self.assertTrue(mapping_1 == mapping_2)

        mapping_1.response.manufacturer_id[1] = 0x01
        self.assertTrue(mapping_1 != mapping_2)


##############################################################################################


    def test_mapping_eq_response_none(self):
        mapping_1 = ClientParameterMapping(
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0x09]
            )
        )

        mapping_2 = ClientParameterMapping(
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            )
        )

        self.assertTrue(mapping_1 != mapping_2)


##############################################################################################


    def test_mapping_eq_request(self):
        mapping_1 = ClientParameterMapping(
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            )
        )

        mapping_2 = ClientParameterMapping(
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            )
        )

        self.assertFalse(mapping_1 == None)
        self.assertFalse(None == mapping_2)

        self.assertTrue(mapping_1 == mapping_2)

        mapping_2.request.data[1] = 0x01
        self.assertTrue(mapping_1 != mapping_2)

        mapping_2.request.data[1] = 0x07
        self.assertTrue(mapping_1 == mapping_2)

        mapping_1.request.manufacturer_id[1] = 0x01
        self.assertTrue(mapping_1 != mapping_2)


##############################################################################################


    def test_mapping_eq_request_none(self):
        mapping_1 = ClientParameterMapping(
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            )        )

        mapping_2 = ClientParameterMapping()

        self.assertTrue(mapping_1 != mapping_2)


##############################################################################################


    def test_mapping_eq_set(self):
        mapping_1 = ClientParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            )
        )

        mapping_2 = ClientParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            )
        )

        self.assertTrue(mapping_1 == mapping_2)

        mapping_2.set.data[1] = 0x03
        self.assertTrue(mapping_1 != mapping_2)


##############################################################################################


    def test_mapping_eq_set_none(self):
        mapping_1 = ClientParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            )
        )

        mapping_2 = ClientParameterMapping()

        self.assertTrue(mapping_1 != mapping_2)


##############################################################################################


    def test_mapping_eq_all_none(self):
        mapping_1 = ClientParameterMapping()
        mapping_2 = ClientParameterMapping()

        self.assertTrue(mapping_1 != mapping_2)


##############################################################################################


    #def test_request_invalid_mappings(self):
        #with self.assertRaises(Exception):           
        #    ClientRequest(
        #        MockClient(),
        #        ClientParameterMapping(),
        #        400
        #    )

        #with self.assertRaises(Exception):           
        #    ClientRequest(
        #        MockClient(),
        #        ClientParameterMapping(
        #            request = SystemExclusive(
        #                manufacturer_id = [0x00, 0x10, 0x20],
        #                data = [0x05, 0x07, 0x09]
        #            )
        #        ),
        #        400
        #    )

        #with self.assertRaises(Exception):           
        #    ClientRequest(
        #        MockClient(),
        #        ClientParameterMapping(
        #            request = ControlChange(2, 3),
        #            response = SystemExclusive(
        #                manufacturer_id = [0x00, 0x10, 0x20],
        #                data = [0x05, 0x07, 0x09]
        #            )
        #        ),
        #        400
        #    )

        #with self.assertRaises(Exception):           
        #    ClientRequest(
        #        MockClient(),
        #        ClientParameterMapping(
        #            request = SystemExclusive(
        #                manufacturer_id = [0x00, 0x10, 0x20],
        #                data = [0x05, 0x07, 0x09]
        #            ),
        #            response = ControlChange(2, 3)
        #        ),
        #        400
        #    )

        