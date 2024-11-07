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
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "gc": MockGC()
}):

    from lib.pyswitch.controller.actions.actions import HoldAction
    from lib.pyswitch.misc import Updater
    from .mocks_appl import MockAction, MockPeriodCounter


class MockController(Updater):
    def __init__(self, config = {}):
        super().__init__()
        
        self.config = config


class MockFootSwitch:
    def __init__(self):
        self.id = "foo"


class TestActionPushButton(unittest.TestCase):


    def test(self):
        hold_period = MockPeriodCounter()

        action_1 = MockAction()
        action_2 = MockAction()
        action_3 = MockAction()
    
        action_hold = HoldAction(
            {
                "actions": [
                    action_1,
                    action_2
                ],
                "actionsHold": action_3
            },
            hold_period
        )

        appl = MockController()

        action_hold.init(appl, MockFootSwitch())

        self.assertEqual(len(appl.updateables), 3)
        self.assertIn(action_1, appl.updateables)
        self.assertIn(action_2, appl.updateables)
        self.assertIn(action_3, appl.updateables)

        self.assertEqual(len(action_hold.get_all_actions()), 4)
        self.assertIn(action_hold, action_hold.get_all_actions())
        self.assertIn(action_1, action_hold.get_all_actions())
        self.assertIn(action_2, action_hold.get_all_actions())
        self.assertIn(action_3, action_hold.get_all_actions())

        # Short press
        action_hold.push()
        action_hold.release()

        self.assertEqual(action_1.num_push_calls, 1)
        self.assertEqual(action_1.num_release_calls, 1)
        
        self.assertEqual(action_2.num_push_calls, 1)
        self.assertEqual(action_2.num_release_calls, 1)

        self.assertEqual(action_3.num_push_calls, 0)
        self.assertEqual(action_3.num_release_calls, 0)
        
        # Long press (no update in between)
        action_hold.push()        
        hold_period.exceed_next_time = True
        action_hold.release()

        self.assertEqual(action_1.num_push_calls, 1)
        self.assertEqual(action_1.num_release_calls, 1)
        
        self.assertEqual(action_2.num_push_calls, 1)
        self.assertEqual(action_2.num_release_calls, 1)

        self.assertEqual(action_3.num_push_calls, 1)
        self.assertEqual(action_3.num_release_calls, 1)

        # Long press (updates in between)
        action_hold.push()        
        hold_period.exceed_next_time = True
        action_hold.update()
        action_hold.update()

        self.assertEqual(action_1.num_push_calls, 1)
        self.assertEqual(action_1.num_release_calls, 1)
        
        self.assertEqual(action_2.num_push_calls, 1)
        self.assertEqual(action_2.num_release_calls, 1)

        self.assertEqual(action_3.num_push_calls, 2)
        self.assertEqual(action_3.num_release_calls, 2)

        action_hold.release()
        action_hold.update()

        self.assertEqual(action_1.num_push_calls, 1)
        self.assertEqual(action_1.num_release_calls, 1)
        
        self.assertEqual(action_2.num_push_calls, 1)
        self.assertEqual(action_2.num_release_calls, 1)

        self.assertEqual(action_3.num_push_calls, 2)
        self.assertEqual(action_3.num_release_calls, 2)

        # Short press again
        action_hold.push()
        action_hold.release()

        self.assertEqual(action_1.num_push_calls, 2)
        self.assertEqual(action_1.num_release_calls, 2)
        
        self.assertEqual(action_2.num_push_calls, 2)
        self.assertEqual(action_2.num_release_calls, 2)

        self.assertEqual(action_3.num_push_calls, 2)
        self.assertEqual(action_3.num_release_calls, 2)


    def test_enable_sub_actions(self):
        action_1 = MockAction()
        action_2 = MockAction()
        action_3 = MockAction()
    
        action_hold = HoldAction(
            {
                "actions": [
                    action_1,
                    action_2
                ],
                "actionsHold": action_3
            }
        )

        appl = MockController()
        action_hold.init(appl, MockFootSwitch())

        self.assertEqual(action_hold.enabled, True)
        self.assertEqual(action_1.enabled, True)
        self.assertEqual(action_2.enabled, True)
        self.assertEqual(action_3.enabled, True)

        action_hold.enabled = False

        self.assertEqual(action_hold.enabled, False)
        self.assertEqual(action_1.enabled, False)
        self.assertEqual(action_2.enabled, False)
        self.assertEqual(action_3.enabled, False)

        action_hold.enabled = True

        self.assertEqual(action_hold.enabled, True)
        self.assertEqual(action_1.enabled, True)
        self.assertEqual(action_2.enabled, True)
        self.assertEqual(action_3.enabled, True)


    def test_minimal(self):
        # Must not throw
        action_hold = HoldAction()
        action_hold.init(MockController(), MockFootSwitch())

        self.assertEqual(action_hold._period_hold.interval, HoldAction.DEFAULT_HOLD_TIME_MILLIS)


    def test_reset(self):
        action_1 = MockAction()
        action_2 = MockAction()
        action_3 = MockAction()
    
        action_hold = HoldAction(
            {
                "actions": [
                    action_1,
                    action_2
                ],
                "actionsHold": action_3
            }
        )

        appl = MockController()
        action_hold.init(appl, MockFootSwitch())

        action_1.num_reset_calls = 0
        action_2.num_reset_calls = 0
        action_3.num_reset_calls = 0

        action_hold.reset()

        self.assertEqual(action_1.num_reset_calls, 1)
        self.assertEqual(action_2.num_reset_calls, 1)
        self.assertEqual(action_3.num_reset_calls, 1)

        action_hold.reset()

        self.assertEqual(action_1.num_reset_calls, 2)
        self.assertEqual(action_2.num_reset_calls, 2)
        self.assertEqual(action_3.num_reset_calls, 2)


    def test_update_displays(self):
        action_1 = MockAction()
        action_2 = MockAction()
        action_3 = MockAction()
    
        action_hold = HoldAction(
            {
                "actions": [
                    action_1,
                    action_2
                ],
                "actionsHold": action_3
            }
        )

        appl = MockController()
        action_hold.init(appl, MockFootSwitch())

        action_1.num_update_displays_calls = 0
        action_2.num_update_displays_calls = 0
        action_3.num_update_displays_calls = 0

        action_hold.update_displays()

        self.assertEqual(action_1.num_update_displays_calls, 1)
        self.assertEqual(action_2.num_update_displays_calls, 1)
        self.assertEqual(action_3.num_update_displays_calls, 1)

        action_hold.update_displays()

        self.assertEqual(action_1.num_update_displays_calls, 2)
        self.assertEqual(action_2.num_update_displays_calls, 2)
        self.assertEqual(action_3.num_update_displays_calls, 2)


    def test_reset_display(self):
        action_1 = MockAction()
        action_2 = MockAction()
        action_3 = MockAction()
    
        action_hold = HoldAction(
            {
                "actions": [
                    action_1,
                    action_2
                ],
                "actionsHold": action_3
            }
        )

        appl = MockController()
        action_hold.init(appl, MockFootSwitch())

        action_1.num_reset_display_calls = 0
        action_2.num_reset_display_calls = 0
        action_3.num_reset_display_calls = 0

        action_hold.reset_display()

        self.assertEqual(action_1.num_reset_display_calls, 1)
        self.assertEqual(action_2.num_reset_display_calls, 1)
        self.assertEqual(action_3.num_reset_display_calls, 1)

        action_hold.reset_display()

        self.assertEqual(action_1.num_reset_display_calls, 2)
        self.assertEqual(action_2.num_reset_display_calls, 2)
        self.assertEqual(action_3.num_reset_display_calls, 2)


    def test_force_update(self):
        action_1 = MockAction()
        action_2 = MockAction()
        action_3 = MockAction()
    
        action_hold = HoldAction(
            {
                "actions": [
                    action_1,
                    action_2
                ],
                "actionsHold": action_3
            }
        )

        appl = MockController()
        action_hold.init(appl, MockFootSwitch())

        action_1.num_force_update_calls = 0
        action_2.num_force_update_calls = 0
        action_3.num_force_update_calls = 0

        action_hold.force_update()

        self.assertEqual(action_1.num_force_update_calls, 1)
        self.assertEqual(action_2.num_force_update_calls, 1)
        self.assertEqual(action_3.num_force_update_calls, 1)

        action_hold.force_update()

        self.assertEqual(action_1.num_force_update_calls, 2)
        self.assertEqual(action_2.num_force_update_calls, 2)
        self.assertEqual(action_3.num_force_update_calls, 2)
