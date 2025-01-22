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
    from .mocks_misc import MockMisc
    from .mocks_callback import *

    with patch.dict(sys.modules, {
        "lib.pyswitch.misc": MockMisc
    }):
        
        from lib.pyswitch.controller.InputControllers import ContinuousController
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

        input = ContinuousController(appl, {
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
        

