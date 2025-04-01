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
    from lib.pyswitch.ui.elements import DisplayLabel
    from lib.pyswitch.controller.callbacks import BinaryParameterCallback
    from lib.pyswitch.misc import Updater
    
    from .mocks_appl import *
    from .mocks_callback import *

    from lib.pyswitch.clients.kemper.actions.tempo import *
    from lib.pyswitch.clients.kemper.mappings.tempo import *


class MockController2(Updater):
    def __init__(self):
        Updater.__init__(self)
        self.client = MockClient()
        self.config = {}


class TestKemperActionDefinitions(unittest.TestCase):

    def test_show_tempo(self):
        display = DisplayLabel(layout = {
            "font": "foo"
        })

        action = SHOW_TEMPO(
            display = display, 
            color = (4, 5, 6), 
            text = "foo",
            id = 67, 
            use_leds = True
        )

        cb = action.callback
        self.assertIsInstance(cb, BinaryParameterCallback)
        self.assertIsInstance(action, PushButtonAction)

        self.assertEqual(cb.mapping, MAPPING_TEMPO_DISPLAY())
        self.assertEqual(cb._text, "foo")
        self.assertEqual(cb._color, (4, 5, 6))

        self.assertEqual(action.label, display)
        self.assertEqual(action.id, 67)
        self.assertEqual(action.uses_switch_leds, True)

        # Must depend on tuner mode state
        action_ecb = action._Action__enable_callback

        self.assertEqual(action_ecb.enabled(action), True)

        # Tuner enabled
        action_ecb._Callback__mappings[0].value = 1
        self.assertEqual(action_ecb.enabled(action), False)

        # Tuner disabled
        action_ecb._Callback__mappings[0].value = 3
        self.assertEqual(action_ecb.enabled(action), True)

        action_ecb._Callback__mappings[0].value = 0
        self.assertEqual(action_ecb.enabled(action), True)


    def test_show_tempo_with_ecb(self):
        display = DisplayLabel(layout = {
            "font": "foo"
        })

        ecb = MockEnabledCallback()

        action = SHOW_TEMPO(
            display = display, 
            color = (4, 5, 6), 
            text = "foo",
            id = 67, 
            use_leds = True, 
            enable_callback = ecb
        )

        cb = action.callback
        self.assertIsInstance(cb, BinaryParameterCallback)
        self.assertIsInstance(action, PushButtonAction)

        self.assertEqual(cb.mapping, MAPPING_TEMPO_DISPLAY())
        self.assertEqual(cb._text, "foo")
        self.assertEqual(cb._color, (4, 5, 6))

        self.assertEqual(action.label, display)
        self.assertEqual(action.id, 67)
        self.assertEqual(action.uses_switch_leds, True)

        # Must depend on tuner mode state
        action_ecb = action._Action__enable_callback

        ecb.output = True
        self.assertEqual(action_ecb.enabled(action), True)

        ecb.output = False
        self.assertEqual(action_ecb.enabled(action), False)

        ecb.output = True
        self.assertEqual(action_ecb.enabled(action), True)

        # Tuner enabled
        action_ecb._Callback__mappings[0].value = 1
        self.assertEqual(action_ecb.enabled(action), False)

        # Tuner disabled
        action_ecb._Callback__mappings[0].value = 3
        self.assertEqual(action_ecb.enabled(action), True)

        action_ecb._Callback__mappings[0].value = 0
        self.assertEqual(action_ecb.enabled(action), True)
