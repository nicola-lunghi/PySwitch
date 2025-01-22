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
    from .mocks_misc import MockMisc
    from .mocks_callback import *

    with patch.dict(sys.modules, {
        "lib.pyswitch.misc": MockMisc
    }):
        
        from lib.pyswitch.controller.input import InputController, InputAction
        from .mocks_appl import *


class MockController2:
    def __init__(self):
        self.client = MockClient()


##################################################################################################################################


class TestControllerInput(unittest.TestCase):

    def test_actions(self):
        pedal = MockPotentiometer()
        
        action_1 = MockInputAction()
        action_2 = MockInputAction()

        appl = MockController2()

        input = InputController(appl, {
            "assignment": {
                "model": pedal,
            },
            "actions": [
                action_1,
                action_2,
            ]
        })

        self.assertEqual(action_1.init_calls, [appl])
        self.assertEqual(action_2.init_calls, [appl])

        pedal.output = 100
        input.process()

        self.assertEqual(action_1.process_calls, [100])
        self.assertEqual(action_2.process_calls, [100])

        pedal.output = 101
        input.process()

        self.assertEqual(action_1.process_calls, [100, 101])
        self.assertEqual(action_2.process_calls, [100, 101])

        # Disable
        pedal.output = 102
        action_1.enabled = False
        input.process()

        self.assertEqual(action_1.process_calls, [100, 101])
        self.assertEqual(action_2.process_calls, [100, 101, 102])

        pedal.output = 103
        action_1.enabled = True
        action_2.enabled = False
        input.process()

        self.assertEqual(action_1.process_calls, [100, 101, 103])
        self.assertEqual(action_2.process_calls, [100, 101, 102])

        pedal.output = 104
        input.process()

        self.assertEqual(action_1.process_calls, [100, 101, 103, 104])
        self.assertEqual(action_2.process_calls, [100, 101, 102])
        

    #################################################################################

    def test_input_action(self):
        self._test_input_action(
            max_value = 128, 
            num_steps = 128,
            data = [
                (0, 0),
                (128, 0),
                (256, 0),
                (257, 1),
                (384, 1),
                (512, 1),
                (8192, 16),
                (16384, 32),
                (32768, 64),
                (49152, 96),
                (65279, 127),
                (65280, 128),
                (65535, 128)
            ]
        )

        self._test_input_action(
            max_value = 256, 
            num_steps = 128,
            data = [
                (0, 0),
                (256, 0),
                (257, 2),
                (8192, 32),
                (16384, 64),
                (32768, 128),
                (49152, 192),
                (65279, 254),
                (65280, 256),
                (65535, 256) 
            ]
        )

        self._test_input_action(
            max_value = 128, 
            num_steps = 16,
            data = [
                (0, 0),
                (2048, 0),
                (2049, 8),
                (8192, 16),
                (16384, 32),
                (63487, 120),
                (63488, 128),
                (65535, 128)
            ]
        )

        ############################################

        self._test_input_action(
            max_value = 16384, 
            num_steps = 128,
            data = [
                (0, 0),
                (128, 0),
                (256, 0),
                (257, 128),
                (384, 128),
                (512, 128),
                (8192, 2048),
                (16384, 4096),
                (32768, 8192),
                (49152, 12288),
                (65279, 16256),
                (65280, 16384),
                (65535, 16384)
            ]
        )

    def test_input_action_transfer_function(self):
        def transfer(value):
            return round(value / 1024) + 32
        
        self._test_input_action(
            data = [
                (0, 32),
                (128, 32),
                (256, 32),
                (257, 32),
                (384, 32),
                (512, 32),
                (8192, 40),
                (16384, 48),
                (32768, 64),
                (49152, 80),
                (65279, 96),
                (65280, 96),
                (65535, 96)
            ],
            transfer_function = transfer
        )
        
    def _test_input_action(self, data, max_value = 1, num_steps = 1, transfer_function = None):
        mapping = MockParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            )
        )

        action = InputAction(
            mapping = mapping,
            max_value = max_value,
            max_frame_rate = 10,
            num_steps = num_steps,
            transfer_function = transfer_function
        )

        appl = MockController2()
        action.init(appl)

        self.assertEqual(action.enabled, True)
        self.assertEqual(action._InputAction__period.interval, 100)
        self.assertEqual(action._InputAction__mapping, mapping)

        action._InputAction__period = MockPeriodCounter()
        period = action._InputAction__period

        # Call without period exceeding
        action.process(1)
        self.assertEqual(appl.client.set_calls, [])

        exp_set_calls = []
        last_value = None
        for entry in data:
            check_value = entry[0]
            exp_value = entry[1]

            if last_value != exp_value:
                exp_set_calls.append({ 
                    "mapping": mapping,
                    "value": exp_value
                })

            last_value = exp_value

            period.exceed_next_time = True
            action.process(check_value)
            
            self.assertEqual(appl.client.set_calls, exp_set_calls, "Check value: " + repr(check_value)) 

            # Call without period exceeding
            action.process(1)            
            self.assertEqual(appl.client.set_calls, exp_set_calls) 


    #################################################################################

        
    def test_input_action_enable_callback(self):
        mapping = MockParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            )
        )

        ecb = MockEnabledCallback(output = True)

        action = InputAction(
            mapping = mapping,
            enable_callback = ecb
        )

        self.assertEqual(action.enabled, True)

        ecb.output = False
        self.assertEqual(action.enabled, False)

        ecb.output = True
        self.assertEqual(action.enabled, True)
