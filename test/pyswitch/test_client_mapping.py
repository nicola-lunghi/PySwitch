from uuid import uuid4
import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

# Import subject under test
with patch.dict(sys.modules, {
    "micropython": MockMicropython,
    "displayio": MockDisplayIO(),
    "adafruit_display_text": MockAdafruitDisplayText(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "adafruit_midi.program_change": MockAdafruitMIDIProgramChange(),
    "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
    "gc": MockGC()
}):
    from adafruit_midi.system_exclusive import SystemExclusive
    from adafruit_midi.control_change import ControlChange
    from adafruit_midi.program_change import ProgramChange

    from pyswitch.controller.client import *


class TestClientParameterMapping(unittest.TestCase):

    def test_private_init(self):
        with self.assertRaises(Exception):
            ClientParameterMapping(name = "footest", create_key = 1)

    def test_singleton_name_check(self):
        ClientParameterMapping.get(name = "footest")

        with self.assertRaises(Exception):
            ClientParameterMapping(name = "footest")

    def test_no_name(self):
        with self.assertRaises(Exception):
            ClientParameterMapping.get(name = None)


    #####################################################################################

    def test_parse_sysex(self):
        msg_irrelevant_man_id = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x21],
            data = [0x00, 0x00, 0xd9, 0x01, 0x04, 0xaa, 0x00, 0x00]
        )           

        msg_irrelevant_data_1 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0xc9, 0x01, 0x04, 0xaa, 0x00, 0x00]
        )           

        msg_irrelevant_data_2 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0xd9, 0x11, 0x04, 0xaa, 0x00, 0x00]
        )           

        msg_irrelevant_data_3 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0xd9, 0x01, 0xa4, 0xaa, 0x00, 0x00]
        )           

        msg_irrelevant_data_4 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0xd9, 0x01, 0x04, 0xab, 0x00, 0x00]
        )           

        msg_irrelevant_data_short = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0xd9, 0x01]
        )    

        msg_irrelevant_wrong_type_1 = ControlChange(
            control = 1,
            value = 1
        )           

        msg_irrelevant_wrong_type_2 = ProgramChange(
            patch = 11
        )           

        def msg_valid(value_1, value_2, valid_prefix): 
            return SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [
                    0x00 if valid_prefix else 0x01, 
                    0x00 if valid_prefix else 0xaa, 
                    0xd9, 
                    0x01, 
                    0x04, 
                    0xaa,
                    value_1,
                    value_2
                ]
            )            

        mapping = ClientParameterMapping.get(
            name = uuid4(),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0xd9, 0x01, 0x04, 0xaa, 0x00, 0x00]
            )            
        )

        # Valid cases
        self.assertTrue(mapping.parse(msg_valid(0x01, 0x01, True)))
        self.assertEqual(mapping.value, 129)

        self.assertTrue(mapping.parse(msg_valid(0x01, 0x05, False)))
        self.assertEqual(mapping.value, 133)

        # Invalid cases
        mapping.value = 111
        self.assertFalse(mapping.parse(msg_irrelevant_man_id))
        self.assertEqual(mapping.value, 111)
        
        self.assertFalse(mapping.parse(msg_irrelevant_data_1))
        self.assertEqual(mapping.value, 111)

        self.assertFalse(mapping.parse(msg_irrelevant_data_2))
        self.assertEqual(mapping.value, 111)

        self.assertFalse(mapping.parse(msg_irrelevant_data_3))
        self.assertEqual(mapping.value, 111)

        self.assertFalse(mapping.parse(msg_irrelevant_data_4))
        self.assertEqual(mapping.value, 111)

        self.assertFalse(mapping.parse(msg_irrelevant_data_short))
        self.assertEqual(mapping.value, 111)

        self.assertFalse(mapping.parse(msg_irrelevant_wrong_type_1))
        self.assertEqual(mapping.value, 111)

        self.assertFalse(mapping.parse(msg_irrelevant_wrong_type_2))
        self.assertEqual(mapping.value, 111)


####################################################################################################


    def test_parse_sysex_string(self):
        def msg_valid(value): 
            hex_str = [ord(c) for c in list(value)]
            
            return SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [
                    0x00, 
                    0x00, 
                    0xd9, 
                    0x01, 
                    0x04, 
                    0xaa
                ] + hex_str + [0]
            )            
        
        mapping = ClientParameterMapping.get(
            name = uuid4(),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0xd9, 0x01, 0x04, 0xaa]
            ),
            type = ClientParameterMapping.PARAMETER_TYPE_STRING       
        )

        # Valid cases
        self.assertTrue(mapping.parse(msg_valid("foo")))
        self.assertEqual(mapping.value, "foo")

        self.assertTrue(mapping.parse(msg_valid("")))
        self.assertEqual(mapping.value, "")

        self.assertTrue(mapping.parse(msg_valid("foo mit Leerzeichen")))
        self.assertEqual(mapping.value, "foo mit Leerzeichen")


####################################################################################################
 

    def test_parse_control_change(self):
        msg_irrelevant_1 = ControlChange(
            control = 4,
            value = 0
        )           

        msg_irrelevant_2 = ControlChange(
            control = 40,
            value = 0
        )           

        msg_irrelevant_wrong_type_1 =  SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x21],
            data = [0x00, 0x00, 0xd9, 0x01]
        )    

        msg_irrelevant_wrong_type_2 = ProgramChange(
            patch = 11
        )           

        msg_valid = ControlChange(
            control = 1,
            value = 0
        )           
                
        mapping = ClientParameterMapping.get(
            name = uuid4(),
            response = ControlChange(
                control = 1,
                value = 0
            )            
        )

        # Valid cases
        msg_valid.value = 4
        self.assertTrue(mapping.parse(msg_valid))
        self.assertEqual(mapping.value, 4)

        msg_valid.value = 6
        self.assertTrue(mapping.parse(msg_valid))
        self.assertEqual(mapping.value, 6)

        # Invalid cases
        mapping.value = 111
        self.assertFalse(mapping.parse(msg_irrelevant_1))
        self.assertEqual(mapping.value, 111)

        self.assertFalse(mapping.parse(msg_irrelevant_2))
        self.assertEqual(mapping.value, 111)

        self.assertFalse(mapping.parse(msg_irrelevant_wrong_type_1))
        self.assertEqual(mapping.value, 111)

        self.assertFalse(mapping.parse(msg_irrelevant_wrong_type_2))
        self.assertEqual(mapping.value, 111)


####################################################################################################


    def test_parse_program_change(self):
        msg_irrelevant_wrong_type_1 =  SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x21],
            data = [0x00, 0x00, 0xd9, 0x01]
        )    

        msg_irrelevant_wrong_type_2 = ControlChange(
            control = 1,
            value = 0
        )

        msg_valid = ProgramChange(
            patch = 0
        )
                
        mapping = ClientParameterMapping.get(
            name = uuid4(),
            response = ProgramChange(
                patch = 0
            )   
        )

        # Valid cases
        msg_valid.patch = 4
        self.assertTrue(mapping.parse(msg_valid))
        self.assertEqual(mapping.value, 4)

        msg_valid.patch = 6
        self.assertTrue(mapping.parse(msg_valid))
        self.assertEqual(mapping.value, 6)

        # Invalid cases
        mapping.value = 111
        self.assertFalse(mapping.parse(msg_irrelevant_wrong_type_1))
        self.assertEqual(mapping.value, 111)

        self.assertFalse(mapping.parse(msg_irrelevant_wrong_type_2))
        self.assertEqual(mapping.value, 111)


####################################################################################################


    def test_parse_other(self):         
        mapping = ClientParameterMapping.get(
            name = uuid4(),
            response = ProgramChange(
                patch = 0
            )   
        )

        # Parse some object guaranteed to not be a midi message ;)
        self.assertFalse(mapping.parse(self))  


####################################################################################################


    def test_set_value_sysex_numeric(self):
        mapping = ClientParameterMapping.get(
            name = uuid4(),
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0xd9, 0x01, 0x04, 0xaa]
            )            
        )

        mapping.set_value(0)
        self.assertEqual(mapping.set.data[6], 0)
        self.assertEqual(mapping.set.data[7], 0)

        mapping.set_value(1)
        self.assertEqual(mapping.set.data[6], 0)
        self.assertEqual(mapping.set.data[7], 1)

        mapping.set_value(127)
        self.assertEqual(mapping.set.data[6], 0)
        self.assertEqual(mapping.set.data[7], 127)

        mapping.set_value(128)
        self.assertEqual(mapping.set.data[6], 1)
        self.assertEqual(mapping.set.data[7], 0)

        mapping.set_value(129)
        self.assertEqual(mapping.set.data[6], 1)
        self.assertEqual(mapping.set.data[7], 1)

        mapping.set_value(255)
        self.assertEqual(mapping.set.data[6], 1)
        self.assertEqual(mapping.set.data[7], 127)

        mapping.set_value(256)
        self.assertEqual(mapping.set.data[6], 2)
        self.assertEqual(mapping.set.data[7], 0)

        mapping.set_value(257)
        self.assertEqual(mapping.set.data[6], 2)
        self.assertEqual(mapping.set.data[7], 1)

        self.assertEqual(list(mapping.set.data[0:6]), [0x00, 0x00, 0xd9, 0x01, 0x04, 0xaa])


    def test_set_value_sysex_string(self):
        mapping = ClientParameterMapping.get(
            name = uuid4(),
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0xd9, 0x01, 0x04, 0xaa]
            ),
            type = ClientParameterMapping.PARAMETER_TYPE_STRING
        )

        with self.assertRaises(Exception):
            mapping.set_value("foo")
        

    def test_set_value_control_change(self):
        mapping = ClientParameterMapping.get(
            name = uuid4(),
            set = ControlChange(
                control = 8,
                value = 0
            )      
        )

        mapping.set_value(0)
        self.assertEqual(mapping.set.value, 0)

        mapping.set_value(1)
        self.assertEqual(mapping.set.value, 1)

        mapping.set_value(127)
        self.assertEqual(mapping.set.value, 127)

        self.assertEqual(mapping.set.control, 8)


    def test_set_value_program_change(self):
        mapping = ClientParameterMapping.get(
            name = uuid4(),
            set = ProgramChange(
                patch = 8
            )      
        )

        mapping.set_value(0)
        self.assertEqual(mapping.set.patch, 0)

        mapping.set_value(1)
        self.assertEqual(mapping.set.patch, 1)

        mapping.set_value(127)
        self.assertEqual(mapping.set.patch, 127)


    def test_set_value_other(self):
        class FooMessage:
            def __init__(self, value):
                self.value = value

        mapping = ClientParameterMapping.get(
            name = uuid4(),
            set = FooMessage(9) 
        )

        mapping.set_value(0)
        self.assertEqual(mapping.set.value, 9)

        mapping.set_value(1)
        self.assertEqual(mapping.set.value, 9)


####################################################################################################


    def test_set_value_list(self):
        mapping = ClientParameterMapping.get(
            name = uuid4(),
            set = [
                ProgramChange(
                    patch = 8
                ),
                ControlChange(
                    control = 19,
                    value = 0
                )
            ]
        )

        mapping.set_value([0, 0])
        self.assertEqual(mapping.set[0].patch, 0)
        self.assertEqual(mapping.set[1].value, 0)

        mapping.set_value([0, 1])
        self.assertEqual(mapping.set[0].patch, 0)
        self.assertEqual(mapping.set[1].value, 1)

        mapping.set_value([1, 0])
        self.assertEqual(mapping.set[0].patch, 1)
        self.assertEqual(mapping.set[1].value, 0)

        mapping.set_value([127, 126])
        self.assertEqual(mapping.set[0].patch, 127)
        self.assertEqual(mapping.set[1].value, 126)
        
        self.assertEqual(mapping.set[1].control, 19)


####################################################################################################
####################################################################################################


    def test_parse_2part(self):
        def msg_sysex_valid(value_1, value_2): 
            return SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [
                    0x00, 
                    0x00, 
                    0xd9, 
                    0x01, 
                    0x04, 
                    0xaa,
                    value_1,
                    value_2
                ]
            )            

        mapping = ClientTwoPartParameterMapping.get(
            name = uuid4(),
            response = [
                ControlChange(
                    control = 112,
                    value = 0
                ),
                SystemExclusive(
                    manufacturer_id = [0x00, 0x10, 0x20],
                    data = [0x00, 0x00, 0xd9, 0x01, 0x04, 0xaa, 0x00]
                )
            ]         
        )

        self.assertEqual(mapping.result_finished(), True)

        self.assertFalse(mapping.parse(msg_sysex_valid(2, 2)))
        self.assertEqual(mapping.result_finished(), True)

        self.assertTrue(mapping.parse(ControlChange(control = 112, value = 10)))
        self.assertEqual(mapping.result_finished(), False)
        self.assertEqual(mapping.value, None)

        self.assertTrue(mapping.parse(msg_sysex_valid(0, 3)))
        self.assertEqual(mapping.result_finished(), True)
        self.assertEqual(mapping.value, 10 * 128 + 3)

        self.assertTrue(mapping.parse(ControlChange(control = 112, value = 11)))
        self.assertEqual(mapping.result_finished(), False)
        self.assertEqual(mapping.value, 10 * 128 + 3)

        self.assertTrue(mapping.parse(msg_sysex_valid(0, 34)))
        self.assertEqual(mapping.result_finished(), True)
        self.assertEqual(mapping.value, 11 * 128 + 34)

