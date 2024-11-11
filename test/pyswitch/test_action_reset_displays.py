import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

# Import subject under test
with patch.dict(sys.modules, {
    "micropython": MockMicropython,
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "gc": MockGC()
}):
    from lib.pyswitch.controller.actions.actions import ResetDisplaysAction



class MockController:
    def __init__(self, config = {}):
        self.config = config
        self.reset_switches_calls = []
        self.reset_display_areas_calls = 0

    def reset_switches(self, ignore_switches_list = []):
        self.reset_switches_calls.append({
            "ignore": ignore_switches_list
        })

    def reset_display_areas(self):
        self.reset_display_areas_calls += 1


class MockFootSwitch:
    pass


class TestActionResetDisplays(unittest.TestCase):

    def test_reset_switches(self):
        appl = MockController()
        action_1 = ResetDisplaysAction({
            "id": "mock",
            "resetSwitches": True
        })
        action_1.init(appl, None)

        action_1.push()

        self.assertEqual(appl.reset_switches_calls[0], {
            "ignore": []
        })


    def test_reset_switches_ignore_own(self):
        appl = MockController()
        sw = MockFootSwitch()
        action_1 = ResetDisplaysAction({
            "id": "mock",
            "resetSwitches": True,
            "ignoreOwnSwitch": True
        })
        action_1.init(appl, sw)

        action_1.push()

        self.assertEqual(appl.reset_switches_calls[0], {
            "ignore": [sw]
        })


    def test_reset_displays(self):
        appl = MockController()
        action_1 = ResetDisplaysAction({
            "id": "mock",
            "resetDisplayAreas": True
        })
        action_1.init(appl, None)

        action_1.push()

        self.assertEqual(appl.reset_display_areas_calls, 1)
