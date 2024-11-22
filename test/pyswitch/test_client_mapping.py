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
    from adafruit_midi.system_exclusive import SystemExclusive
    from.mocks_appl import *


class MockParameterMapping2(MockParameterMapping):
    pass

class MockClient:
    def __init__(self):
        self.debug = False


class TestClientMapping(unittest.TestCase):


    def test_eq_different_types(self):
        mapping_1 = MockParameterMapping(
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0x09]
            )
        )

        mapping_2 = MockParameterMapping2(
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0x09]
            )
        )

        self.assertFalse(mapping_1 == None)
        self.assertFalse(None == mapping_2)

        self.assertTrue(mapping_1 != mapping_2)
        
        
##############################################################################################


    def test_eq_response(self):
        mapping_1 = MockParameterMapping(
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


    def test_eq_response_list(self):
        mapping_1 = MockParameterMapping(
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            ),
            response = [
                SystemExclusive(
                    manufacturer_id = [0x00, 0x10, 0x20],
                    data = [0x00, 0x00, 0x09]
                ),
                SystemExclusive(
                    manufacturer_id = [0x00, 0x10, 0x30],
                    data = [0x77, 0x00, 0x09]
                )
            ]
        )

        mapping_2 = MockParameterMapping(
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x10]
            ),
            response = [
                SystemExclusive(
                    manufacturer_id = [0x00, 0x10, 0x20],
                    data = [0x00, 0x00, 0x09]
                ),
                SystemExclusive(
                    manufacturer_id = [0x00, 0x10, 0x30],
                    data = [0x77, 0x00, 0x09]
                )
            ]
        )

        self.assertFalse(mapping_1 == None)
        self.assertFalse(None == mapping_2)

        self.assertTrue(mapping_1 == mapping_2)

        mapping_2.response[0].data[1] = 0x01
        self.assertTrue(mapping_1 != mapping_2)

        mapping_2.response[0].data[1] = 0x00
        self.assertTrue(mapping_1 == mapping_2)

        mapping_1.response[1].manufacturer_id[1] = 0x01
        self.assertTrue(mapping_1 != mapping_2)

        mapping_1.response[1].manufacturer_id[1] = 0x10
        self.assertTrue(mapping_1 == mapping_2)

        mapping_1.response = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0x09]
        )

        self.assertTrue(mapping_1 != mapping_2)

        mapping_1.response = [
            SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0x09]
            ),
            SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x30],
                data = [0x77, 0x00, 0x09]
            ),
            SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x30],
                data = [0x77, 0x00, 0x09]
            )
        ]

        self.assertTrue(mapping_1 != mapping_2)


##############################################################################################


    def test_eq_response_none(self):
        mapping_1 = MockParameterMapping(
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
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            )
        )

        self.assertTrue(mapping_1 != mapping_2)


##############################################################################################


    def test_eq_request(self):
        mapping_1 = MockParameterMapping(
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            )
        )

        mapping_2 = MockParameterMapping(
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


    def test_eq_request_list(self):
        mapping_1 = MockParameterMapping(
            request = [
                SystemExclusive(
                    manufacturer_id = [0x00, 0x10, 0x20],
                    data = [0x05, 0x07, 0x09]
                ),
                SystemExclusive(
                    manufacturer_id = [0x00, 0x10, 0x23],
                    data = [0x05, 0x77, 0x09]
                )
            ]
        )

        mapping_2 = MockParameterMapping(
            request = [
                SystemExclusive(
                    manufacturer_id = [0x00, 0x10, 0x20],
                    data = [0x05, 0x07, 0x09]
                ),
                SystemExclusive(
                    manufacturer_id = [0x00, 0x10, 0x23],
                    data = [0x05, 0x77, 0x09]
                )
            ]
        )

        self.assertFalse(mapping_1 == None)
        self.assertFalse(None == mapping_2)

        self.assertTrue(mapping_1 == mapping_2)

        mapping_2.request[0].data[1] = 0x01
        self.assertTrue(mapping_1 != mapping_2)

        mapping_2.request[0].data[1] = 0x07
        self.assertTrue(mapping_1 == mapping_2)

        mapping_1.request[1].manufacturer_id[1] = 0x01
        self.assertTrue(mapping_1 != mapping_2)

        mapping_1.request[1].manufacturer_id[1] = 0x10
        self.assertTrue(mapping_1 == mapping_2)

        mapping_1.request = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x23],
            data = [0x05, 0x77, 0x09]
        )        
        self.assertTrue(mapping_1 != mapping_2)

        mapping_1.request = [
                SystemExclusive(
                    manufacturer_id = [0x00, 0x10, 0x20],
                    data = [0x05, 0x07, 0x09]
                ),
                SystemExclusive(
                    manufacturer_id = [0x00, 0x10, 0x23],
                    data = [0x05, 0x77, 0x09]
                ),
                SystemExclusive(
                    manufacturer_id = [0x00, 0x10, 0x23],
                    data = [0x05, 0x77, 0x09]
                )
            ]
        self.assertTrue(mapping_1 != mapping_2)


##############################################################################################


    def test_eq_request_none(self):
        mapping_1 = MockParameterMapping(
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            )        )

        mapping_2 = MockParameterMapping()

        self.assertTrue(mapping_1 != mapping_2)


##############################################################################################


    def test_eq_set(self):
        mapping_1 = MockParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            )
        )

        mapping_2 = MockParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            )
        )

        self.assertTrue(mapping_1 == mapping_2)

        mapping_2.set.data[1] = 0x03
        self.assertTrue(mapping_1 != mapping_2)


##############################################################################################


    def test_eq_set_list(self):
        mapping_1 = MockParameterMapping(
            set = [
                SystemExclusive(
                    manufacturer_id = [0x00, 0x10, 0x20],
                    data = [0x05, 0x07, 0x09]
                ),
                SystemExclusive(
                    manufacturer_id = [0x00, 0x10, 0x24],
                    data = [0x05, 0x67, 0x09]
                )
            ]
        )

        mapping_2 = MockParameterMapping(
            set = [
                SystemExclusive(
                    manufacturer_id = [0x00, 0x10, 0x20],
                    data = [0x05, 0x07, 0x09]
                ),
                SystemExclusive(
                    manufacturer_id = [0x00, 0x10, 0x24],
                    data = [0x05, 0x67, 0x09]
                )
            ]
        )

        self.assertTrue(mapping_1 == mapping_2)

        mapping_2.set[1].data[1] = 0x03
        self.assertTrue(mapping_1 != mapping_2)

        mapping_2.set[1].data[1] = 0x67
        self.assertTrue(mapping_1 == mapping_2)

        mapping_2.set = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x24],
            data = [0x05, 0x67, 0x09]
        )
        self.assertTrue(mapping_1 != mapping_2)

        mapping_2.et = [
            SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            ),
            SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x24],
                data = [0x05, 0x67, 0x09]
            ),
            SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x24],
                data = [0x05, 0x67, 0x09]
            )
        ]
        self.assertTrue(mapping_1 != mapping_2)


##############################################################################################


    def test_eq_set_none(self):
        mapping_1 = MockParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            )
        )

        mapping_2 = MockParameterMapping()

        self.assertTrue(mapping_1 != mapping_2)


##############################################################################################


    def test_eq_all_none(self):
        mapping_1 = MockParameterMapping()
        mapping_2 = MockParameterMapping()

        self.assertTrue(mapping_1 != mapping_2)

