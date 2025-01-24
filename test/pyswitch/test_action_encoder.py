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
    from adafruit_midi.control_change import ControlChange
    
    from .mocks_misc import MockMisc
    from .mocks_callback import *

    with patch.dict(sys.modules, {
        "lib.pyswitch.misc": MockMisc
    }):
        
        from lib.pyswitch.controller.EncoderAction import EncoderAction
        from .mocks_appl import *


class MockController2:
    def __init__(self):
        self.client = MockClient()


##################################################################################################################################


class TestEncoderAction(unittest.TestCase):

    def test_fix_range(self):
        self._test(
            max_value = 1023,
            step_width = 16,
            start_pos = 4, 
            start_value = 100, 
            data = [
                (5, 116),
                (6, 132),
                (7, 148),
                (54, 900),
                (61, 1012),
                (62, 1023),
                (65, 1023),
                (10000, 1023),
                (9999, 1007),
                (9989, 847),
                (9937, 15),
                (9936, 0),
                (9910, 0),
                (1, 0),
                (2, 16),
                (3, 32),
                (5, 64)
            ]
        )

        self._test(
            max_value = 127,
            step_width = 1,
            start_pos = 4, 
            start_value = 100, 
            data = [
                (5, 101),
                (6, 102),
                (7, 103),
                (24, 120),
                (31, 127),
                (61, 127),
                (62, 127),
                (65, 127),
                (10000, 127),
                (9999, 126),
                (9989, 116),
                (9919, 46),
                (9900, 27),
                (9873, 0),
                (9872, 0),
                (1, 0),
                (2, 1),
                (20, 19)
            ]
        )


    def test_auto_range(self):
        self._test(
            cc_mapping = False,
            max_value = None,
            step_width = None,
            start_pos = 0, 
            start_value = 0, 
            data = [
                (1, 160),
                (2, 320),
                (3, 480),
                (102, 16320),
                (103, 16383),
                (104, 16383),
                (10000, 16383),
                (9999, 16223),
                (9989, 14623),
                (9916, 2943),
                (9898, 63),
                (9897, 0),
                (1, 0),
                (2, 160),
                (3, 320),
                (5, 640)
            ]
        )

        self._test(
            cc_mapping = True,
            max_value = None,
            step_width = None,
            start_pos = 4, 
            start_value = 100, 
            data = [
                (5, 101),
                (6, 102),
                (7, 103),
                (24, 120),
                (31, 127),
                (61, 127),
                (62, 127),
                (65, 127),
                (10000, 127),
                (9999, 126),
                (9989, 116),
                (9919, 46),
                (9900, 27),
                (9873, 0),
                (9872, 0),
                (1, 0),
                (2, 1),
                (20, 19)
            ]
        )

    def _test(self, max_value, step_width, start_pos, start_value, data, cc_mapping = False):
        self._do_test(
            max_value = max_value,
            step_width = step_width,
            start_pos = start_pos,
            start_value = start_value,
            data = data,
            cc_mapping = cc_mapping,
            mapping_with_response = True
        )

        self._do_test(
            max_value = max_value,
            step_width = step_width,
            start_pos = start_pos,
            start_value = start_value,
            data = data,
            cc_mapping = cc_mapping,
            mapping_with_response = False
        )

    def _do_test(self, max_value, step_width, start_pos, start_value, data, cc_mapping, mapping_with_response):
        if not cc_mapping:
            mapping = MockParameterMapping(
                set = SystemExclusive(
                    manufacturer_id = [0x00, 0x10, 0x20],
                    data = [0x05, 0x07, 0x09]
                ),
                response = None if not mapping_with_response else SystemExclusive(
                    manufacturer_id = [0x00, 0x11, 0x20],
                    data = [0x05, 0x07, 0x03]
                )
            )
        else:
            mapping = MockParameterMapping(
                set = ControlChange(20, 1),
                response = None if not mapping_with_response else ControlChange(20, 1)
            )

        action = EncoderAction(
            mapping = mapping,
            max_value = max_value,
            step_width = step_width
        )

        appl = MockController2()
        action.init(appl)

        self.assertEqual(action.enabled, True)
        self.assertEqual(action._EncoderAction__mapping, mapping)
        
        if mapping_with_response or start_value != 0:
            mapping.value = start_value

        # Start position (only catches the current mapping value and exits)
        action.process(start_pos)
        self.assertEqual(appl.client.last_sent_message, None) 

        for entry in data:
            position = entry[0]
            exp_value = entry[1]

            action.process(position)
            self.assertEqual(appl.client.last_sent_message, { "mapping": mapping, "value": exp_value }, repr(entry))
            
            # Simulate that the mapping value had been changed by an incoming message
            if mapping_with_response:
                mapping.value = exp_value


        # None
        if mapping_with_response:
            mapping.value = None
            
            appl.client.set_calls = []
            action.process(7865)
            
            self.assertEqual(appl.client.last_sent_message, None)


    def test_none_value(self):
        mapping = MockParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            )
        )

        action = EncoderAction(
            mapping = mapping
        )

        appl = MockController2()
        action.init(appl)

        self.assertEqual(action.enabled, True)
        self.assertEqual(action._EncoderAction__mapping, mapping)
        
        mapping.value = None

        # Start position (only catches the current mapping value and exits)
        action.process(98)
        self.assertEqual(appl.client.last_sent_message, None) 


    #################################################################################


    def test_update(self):
        mapping = MockParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            ),
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x17, 0x09]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x21],
                data = [0x05, 0x07, 0x10]
            )
        )

        action = EncoderAction(
            mapping = mapping
        )

        appl = MockController2()
        action.init(appl)

        action.update()
        self.assertEqual(appl.client.request_calls, [{ "mapping": mapping, "listener": None }]) 

        action.update()
        self.assertEqual(appl.client.request_calls, [{ "mapping": mapping, "listener": None }, { "mapping": mapping, "listener": None }]) 
        

    #################################################################################

        
    def test_enable_callback(self):
        mapping = MockParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            )
        )

        ecb = MockEnabledCallback(output = True)

        action = EncoderAction(
            mapping = mapping,
            enable_callback = ecb
        )

        self.assertEqual(action.enabled, True)

        ecb.output = False
        self.assertEqual(action.enabled, False)

        ecb.output = True
        self.assertEqual(action.enabled, True)


    