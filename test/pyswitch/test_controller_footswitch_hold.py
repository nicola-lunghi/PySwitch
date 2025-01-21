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

    from lib.pyswitch.controller.FootSwitchController import FootSwitchController
    from lib.pyswitch.misc import Updater

    from .mocks_appl import MockAction, MockPeriodCounter, MockSwitch
    from .mocks_callback import *


class MockController2(Updater):
    def __init__(self, config = {}):
        super().__init__()
        
        self.config = config


class TestFootswitchControllerHold(unittest.TestCase):

    def test(self):
        hold_period = MockPeriodCounter()
        switch = MockSwitch()

        action_1 = MockAction()
        action_2 = MockAction()
        action_3 = MockAction()
    
        appl = MockController2()

        fs = FootSwitchController(
            appl,
            {
                "assignment": {
                    "model": switch
                },
                "actions": [
                    action_1,
                    action_2
                ],
                "actionsHold": [
                    action_3
                ]
            },
            hold_period
        )

        self.assertEqual(fs.actions, [action_1, action_2, action_3])

        # Short press
        switch.shall_be_pushed = True
        fs.process()

        self.assertEqual(action_1.num_push_calls, 0)
        self.assertEqual(action_1.num_release_calls, 0)

        self.assertEqual(action_2.num_push_calls, 0)
        self.assertEqual(action_2.num_release_calls, 0)

        self.assertEqual(action_3.num_push_calls, 0)
        self.assertEqual(action_3.num_release_calls, 0)

        switch.shall_be_pushed = False
        fs.process()

        self.assertEqual(action_1.num_push_calls, 1)
        self.assertEqual(action_1.num_release_calls, 1)
        
        self.assertEqual(action_2.num_push_calls, 1)
        self.assertEqual(action_2.num_release_calls, 1)

        self.assertEqual(action_3.num_push_calls, 0)
        self.assertEqual(action_3.num_release_calls, 0)
        
        # Long press
        switch.shall_be_pushed = True
        fs.process()

        self.assertEqual(action_1.num_push_calls, 1)
        self.assertEqual(action_1.num_release_calls, 1)
        
        self.assertEqual(action_2.num_push_calls, 1)
        self.assertEqual(action_2.num_release_calls, 1)

        self.assertEqual(action_3.num_push_calls, 0)
        self.assertEqual(action_3.num_release_calls, 0)

        hold_period.exceed_next_time = True
        
        switch.shall_be_pushed = False
        fs.process()

        self.assertEqual(action_1.num_push_calls, 1)
        self.assertEqual(action_1.num_release_calls, 1)
        
        self.assertEqual(action_2.num_push_calls, 1)
        self.assertEqual(action_2.num_release_calls, 1)

        self.assertEqual(action_3.num_push_calls, 1)
        self.assertEqual(action_3.num_release_calls, 1)

        # Short press again
        switch.shall_be_pushed = True
        fs.process()

        self.assertEqual(action_1.num_push_calls, 1)
        self.assertEqual(action_1.num_release_calls, 1)
        
        self.assertEqual(action_2.num_push_calls, 1)
        self.assertEqual(action_2.num_release_calls, 1)

        self.assertEqual(action_3.num_push_calls, 1)
        self.assertEqual(action_3.num_release_calls, 1)

        switch.shall_be_pushed = False
        fs.process()

        self.assertEqual(action_1.num_push_calls, 2)
        self.assertEqual(action_1.num_release_calls, 2)
        
        self.assertEqual(action_2.num_push_calls, 2)
        self.assertEqual(action_2.num_release_calls, 2)

        self.assertEqual(action_3.num_push_calls, 1)
        self.assertEqual(action_3.num_release_calls, 1)

        # Long press with running out of time before release
        switch.shall_be_pushed = True
        fs.process()

        self.assertEqual(action_1.num_push_calls, 2)
        self.assertEqual(action_1.num_release_calls, 2)
        
        self.assertEqual(action_2.num_push_calls, 2)
        self.assertEqual(action_2.num_release_calls, 2)

        self.assertEqual(action_3.num_push_calls, 1)
        self.assertEqual(action_3.num_release_calls, 1)

        hold_period.exceed_next_time = True        
        fs.process()

        self.assertEqual(action_1.num_push_calls, 2)
        self.assertEqual(action_1.num_release_calls, 2)
        
        self.assertEqual(action_2.num_push_calls, 2)
        self.assertEqual(action_2.num_release_calls, 2)

        self.assertEqual(action_3.num_push_calls, 2)
        self.assertEqual(action_3.num_release_calls, 2)


    def test_no_hold(self):
        hold_period = MockPeriodCounter()
        switch = MockSwitch()

        action_1 = MockAction()
        action_2 = MockAction()
    
        appl = MockController2()

        fs = FootSwitchController(
            appl,
            {
                "assignment": {
                    "model": switch
                },
                "actions": [
                    action_1,
                    action_2
                ]
            },
            hold_period
        )

        self.assertEqual(fs.actions, [action_1, action_2])

        # Short press
        switch.shall_be_pushed = True
        fs.process()

        self.assertEqual(action_1.num_push_calls, 1)
        self.assertEqual(action_1.num_release_calls, 0)

        self.assertEqual(action_2.num_push_calls, 1)
        self.assertEqual(action_2.num_release_calls, 0)

        switch.shall_be_pushed = False
        fs.process()

        self.assertEqual(action_1.num_push_calls, 1)
        self.assertEqual(action_1.num_release_calls, 1)
        
        self.assertEqual(action_2.num_push_calls, 1)
        self.assertEqual(action_2.num_release_calls, 1)

        # Long press
        switch.shall_be_pushed = True
        fs.process()

        self.assertEqual(action_1.num_push_calls, 2)
        self.assertEqual(action_1.num_release_calls, 1)
        
        self.assertEqual(action_2.num_push_calls, 2)
        self.assertEqual(action_2.num_release_calls, 1)

        hold_period.exceed_next_time = True
        
        switch.shall_be_pushed = False
        fs.process()

        self.assertEqual(action_1.num_push_calls, 2)
        self.assertEqual(action_1.num_release_calls, 2)
        
        self.assertEqual(action_2.num_push_calls, 2)
        self.assertEqual(action_2.num_release_calls, 2)

        # Short press again
        switch.shall_be_pushed = True
        fs.process()

        self.assertEqual(action_1.num_push_calls, 3)
        self.assertEqual(action_1.num_release_calls, 2)
        
        self.assertEqual(action_2.num_push_calls, 3)
        self.assertEqual(action_2.num_release_calls, 2)

        switch.shall_be_pushed = False
        fs.process()

        self.assertEqual(action_1.num_push_calls, 3)
        self.assertEqual(action_1.num_release_calls, 3)
        
        self.assertEqual(action_2.num_push_calls, 3)
        self.assertEqual(action_2.num_release_calls, 3)


    def test_disabled_actions(self):
        hold_period = MockPeriodCounter()
        switch = MockSwitch()

        ec = MockEnabledCallback(output = False)

        action_1 = MockAction()
        action_2 = MockAction(config = { "enableCallback": ec })
        action_3 = MockAction()
        action_4 = MockAction(config = { "enableCallback": ec })
    
        appl = MockController2()

        fs = FootSwitchController(
            appl,
            {
                "assignment": {
                    "model": switch
                },
                "actions": [
                    action_1,
                    action_2
                ],
                "actionsHold": [
                    action_3,
                    action_4
                ]
            },
            hold_period
        )

        self.assertEqual(fs.actions, [action_1, action_2, action_3, action_4])

        # Short press
        switch.shall_be_pushed = True
        fs.process()

        self.assertEqual(action_1.num_push_calls, 0)
        self.assertEqual(action_1.num_release_calls, 0)

        self.assertEqual(action_2.num_push_calls, 0)
        self.assertEqual(action_2.num_release_calls, 0)

        self.assertEqual(action_3.num_push_calls, 0)
        self.assertEqual(action_3.num_release_calls, 0)

        self.assertEqual(action_4.num_push_calls, 0)
        self.assertEqual(action_4.num_release_calls, 0)

        switch.shall_be_pushed = False
        fs.process()

        self.assertEqual(action_1.num_push_calls, 1)
        self.assertEqual(action_1.num_release_calls, 1)
        
        self.assertEqual(action_2.num_push_calls, 0)
        self.assertEqual(action_2.num_release_calls, 0)

        self.assertEqual(action_3.num_push_calls, 0)
        self.assertEqual(action_3.num_release_calls, 0)
        
        self.assertEqual(action_4.num_push_calls, 0)
        self.assertEqual(action_4.num_release_calls, 0)

        # Long press
        switch.shall_be_pushed = True
        fs.process()

        self.assertEqual(action_1.num_push_calls, 1)
        self.assertEqual(action_1.num_release_calls, 1)
        
        self.assertEqual(action_2.num_push_calls, 0)
        self.assertEqual(action_2.num_release_calls, 0)

        self.assertEqual(action_3.num_push_calls, 0)
        self.assertEqual(action_3.num_release_calls, 0)

        hold_period.exceed_next_time = True
        
        switch.shall_be_pushed = False
        fs.process()

        self.assertEqual(action_1.num_push_calls, 1)
        self.assertEqual(action_1.num_release_calls, 1)
        
        self.assertEqual(action_2.num_push_calls, 0)
        self.assertEqual(action_2.num_release_calls, 0)

        self.assertEqual(action_3.num_push_calls, 1)
        self.assertEqual(action_3.num_release_calls, 1)

        self.assertEqual(action_4.num_push_calls, 0)
        self.assertEqual(action_4.num_release_calls, 0)

        # Short press again
        switch.shall_be_pushed = True
        fs.process()

        self.assertEqual(action_1.num_push_calls, 1)
        self.assertEqual(action_1.num_release_calls, 1)
        
        self.assertEqual(action_2.num_push_calls, 0)
        self.assertEqual(action_2.num_release_calls, 0)

        self.assertEqual(action_3.num_push_calls, 1)
        self.assertEqual(action_3.num_release_calls, 1)

        self.assertEqual(action_4.num_push_calls, 0)
        self.assertEqual(action_4.num_release_calls, 0)

        switch.shall_be_pushed = False
        fs.process()

        self.assertEqual(action_1.num_push_calls, 2)
        self.assertEqual(action_1.num_release_calls, 2)
        
        self.assertEqual(action_2.num_push_calls, 0)
        self.assertEqual(action_2.num_release_calls, 0)

        self.assertEqual(action_3.num_push_calls, 1)
        self.assertEqual(action_3.num_release_calls, 1)

        self.assertEqual(action_4.num_push_calls, 0)
        self.assertEqual(action_4.num_release_calls, 0)


