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
    
    from lib.pyswitch.clients.kemper import KemperActionDefinitions, KemperEffectEnableCallback, KemperEffectSlot, KemperMappings, KemperMorphCallback
    from lib.pyswitch.ui.elements import DisplayLabel
    from lib.pyswitch.controller.callbacks import BinaryParameterCallback
    from lib.pyswitch.misc import Updater
    
    from .mocks_appl import *
    from .mocks_callback import *


class MockController2(Updater):
    def __init__(self, switches = []):
        Updater.__init__(self)
        self.client = MockClient()
        self.config = {}
        self.switches = switches


class MockFootSwitch:
    def __init__(self, actions = []):
        self.override_action = None
        self.actions = actions
        self.pixels = []


class TestKemperActionTunerMode(unittest.TestCase):


    def test_tuner_mode(self):
        display = DisplayLabel(layout = {
            "font": "foo",
            "backColor": (0, 0, 0)
        })

        ecb = MockEnabledCallback(output = True)

        action = KemperActionDefinitions.TUNER_MODE(
            display = display, 
            mode = PushButtonAction.ONE_SHOT, 
            color = (4, 5, 6), 
            id = 67, 
            use_leds = True, 
            enable_callback = ecb
        )

        cb = action.callback
        self.assertIsInstance(cb, KemperActionDefinitions._TunerModeCallback)
        self.assertIsInstance(action, PushButtonAction)

        self.assertEqual(cb._BinaryParameterCallback__mapping, KemperMappings.TUNER_MODE_STATE())
        self.assertEqual(cb._BinaryParameterCallback__text, "Tuner")
        self.assertEqual(cb._BinaryParameterCallback__color, (4, 5, 6))

        self.assertEqual(action.label, display)
        self.assertEqual(action.id, 67)
        self.assertEqual(action.uses_switch_leds, True)
        self.assertEqual(action._Action__enable_callback, ecb)

        switch_action_0 = MockAction()
        switch_action_1 = MockAction()
        switch_action_2 = MockAction()
        switch_action_3 = MockAction()

        switch = MockFootSwitch(
            actions = [
                switch_action_0,
                action
            ]
        )

        switch_other_1 = MockFootSwitch(
            actions = [
                switch_action_1,
                switch_action_2
            ]
        )

        switch_other_2 = MockFootSwitch(
            actions = [
                switch_action_3
            ]
        )

        appl = MockController2(
            switches = [
                switch_other_1,
                switch,
                switch_other_2
            ]
        )
        action.init(appl, switch)
        self.assertTrue(action.enabled)

        # We have to call update_displays because this "dirty hack" allows the callback to get a reference to the action
        action.update_displays()

        mapping = cb._BinaryParameterCallback__mapping

        # Tuner off
        mapping.value = 3
        cb.parameter_changed(mapping)
        
        self.assertEqual(switch.override_action, None)
        self.assertEqual(switch_other_1.override_action, None)
        self.assertEqual(switch_other_2.override_action, None)
        
        #self.assertEqual(action.num_reset_calls, 1)
        self.assertEqual(switch_action_0.num_reset_calls, 1)
        self.assertEqual(switch_action_1.num_reset_calls, 1)
        self.assertEqual(switch_action_2.num_reset_calls, 1)
        self.assertEqual(switch_action_3.num_reset_calls, 1)

        # Tuner on
        mapping.value = 1
        cb.parameter_changed(mapping)
        
        self.assertEqual(switch.override_action, cb)
        self.assertEqual(switch_other_1.override_action, cb)
        self.assertEqual(switch_other_2.override_action, cb)
        
        #self.assertEqual(action.num_reset_calls, 1)
        self.assertEqual(switch_action_0.num_reset_calls, 1)
        self.assertEqual(switch_action_1.num_reset_calls, 1)
        self.assertEqual(switch_action_2.num_reset_calls, 1)
        self.assertEqual(switch_action_3.num_reset_calls, 1)

        # Tuner off again
        mapping.value = 0
        cb.parameter_changed(mapping)
        
        self.assertEqual(switch.override_action, None)
        self.assertEqual(switch_other_1.override_action, None)
        self.assertEqual(switch_other_2.override_action, None)
        
        #self.assertEqual(action.num_reset_calls, 1)
        self.assertEqual(switch_action_0.num_reset_calls, 2)
        self.assertEqual(switch_action_1.num_reset_calls, 2)
        self.assertEqual(switch_action_2.num_reset_calls, 2)
        self.assertEqual(switch_action_3.num_reset_calls, 2)


    def test_state_change_by_user(self):
        action = KemperActionDefinitions.TUNER_MODE()

        switch = MockFootSwitch(
            actions = [
                action
            ]
        )

        appl = MockController2()
        action.init(appl, switch)

        cb = action.callback
        mapping = cb._BinaryParameterCallback__mapping
        self.assertEqual(action.state, False)

        mapping.value = 1
        action.state = True
        self.assertEqual(action.state, True)
        
        self.assertEqual(appl.client.set_calls, [
            {
                "mapping": cb._BinaryParameterCallback__mapping,
                "value": 1
            }
        ])

        appl.client.set_calls = []
        mapping.value = 3
        action.state = False
        self.assertEqual(action.state, False)

        self.assertEqual(appl.client.set_calls, [
            {
                "mapping": cb._BinaryParameterCallback__mapping,
                "value": 0
            }
        ])


    def test_override_action_self(self):
        action = KemperActionDefinitions.TUNER_MODE(
            mode = PushButtonAction.ONE_SHOT
        )

        cb = action.callback

        switch = MockFootSwitch(
            actions = [
                action
            ]
        )
        
        appl = MockController2()
        action.init(appl, switch)

        # Simulate switching the tuner on by PySwitch
        action.state = True

        cb.push()
        cb.release()

        self.assertEqual(appl.client.set_calls, [
            {
                "mapping": cb._BinaryParameterCallback__mapping,
                "value": 1
            }
        ])

        appl.client.set_calls = []

        cb.push()
        cb.release()

        self.assertEqual(appl.client.set_calls, [
            {
                "mapping": cb._BinaryParameterCallback__mapping,
                "value": 0
            }
        ])


    def test_override_action_others(self):
        action = KemperActionDefinitions.TUNER_MODE(
            mode = PushButtonAction.ONE_SHOT
        )

        cb = action.callback

        switch = MockFootSwitch(
            actions = [
                action
            ]
        )
        
        appl = MockController2()
        action.init(appl, switch)

        cb.push()
        cb.release()

        self.assertEqual(appl.client.set_calls, [
            {
                "mapping": cb._BinaryParameterCallback__mapping,
                "value": 0
            }
        ])
