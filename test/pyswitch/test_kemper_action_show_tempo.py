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
    from lib.pyswitch.controller.callbacks import Callback
    
    from .mocks_appl import *
    from .mocks_callback import *

    from lib.pyswitch.clients.kemper.actions.tempo import *
    from lib.pyswitch.clients.kemper.mappings.tempo import *
    

class TestKemperActionDefinitions(unittest.TestCase):

    def test_show_tempo(self):
        with patch.dict(sys.modules, {
            "micropython": MockMicropython,
            "displayio": MockDisplayIO(),
            "adafruit_display_text": MockAdafruitDisplayText(),
            "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
            "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
            "adafruit_midi.program_change": MockAdafruitMIDIProgramChange(),
            "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
            "gc": MockGC()
        }):
            action = SHOW_TEMPO(
                color = (4, 5, 6), 
                id = 67, 
                use_leds = True
            )

            cb = action.callback
            self.assertIsInstance(cb, Callback)
            self.assertIsInstance(action, Action)

            mapping_tempo = MAPPING_TEMPO_DISPLAY()
            mapping_tuner = KemperMappings.TUNER_MODE_STATE()

            self.assertEqual(cb._KemperShowTempoCallback__tempo_mapping, mapping_tempo)
            self.assertEqual(cb._KemperShowTempoCallback__tuner_mapping, mapping_tuner)
            self.assertEqual(cb._color, (4, 5, 6))

            self.assertEqual(action.label, None)
            self.assertEqual(action.id, 67)
            self.assertEqual(action.uses_switch_leds, True)

            # appl = MockController2()
            # switch = MockFootswitch
            # action.init(appl, None)

            # mapping_tempo = 0
            # mapping_tuner.value = 3 # Off

            # action.update_displays()

            # self.assertEqual()

    # def test_show_tempo_display(self):
    #     display = DisplayLabel(layout = {
    #         "font": "foo"
    #     })

    #     with patch.dict(sys.modules, {
    #         "micropython": MockMicropython,
    #         "displayio": MockDisplayIO(),
    #         "adafruit_display_text": MockAdafruitDisplayText(),
    #         "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    #         "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    #         "adafruit_midi.program_change": MockAdafruitMIDIProgramChange(),
    #         "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
    #         "gc": MockGC()
    #     }):
    #         from lib.pyswitch.clients.kemper.mappings.tempo_bpm import MAPPING_TEMPO_BPM

    #         action = SHOW_TEMPO(
    #             display = display, 
    #             color = (4, 5, 6), 
    #             text = "foo {bpm}",
    #             id = 67, 
    #             use_leds = True
    #         )

    #         cb = action.callback
    #         self.assertIsInstance(cb, Callback)
    #         self.assertIsInstance(action, Action)

    #         self.assertEqual(cb._KemperShowTempoCallback__tempo_mapping, MAPPING_TEMPO_DISPLAY())
    #         self.assertEqual(cb._KemperShowTempoCallback__tuner_mapping, KemperMappings.TUNER_MODE_STATE())
    #         self.assertEqual(cb._KemperShowTempoCallback__bpm_mapping, MAPPING_TEMPO_BPM())
    #         self.assertEqual(cb._text, "foo {bpm}")
    #         self.assertEqual(cb._color, (4, 5, 6))

    #         self.assertEqual(action.label, display)
    #         self.assertEqual(action.id, 67)
    #         self.assertEqual(action.uses_switch_leds, True)

    #         # # Must depend on tuner mode state
    #         # action_ecb = action._Action__enable_callback

    #         # self.assertEqual(action_ecb.enabled(action), True)

    #         # # Tuner enabled
    #         # action_ecb._Callback__mappings[0].value = 1
    #         # self.assertEqual(action_ecb.enabled(action), False)

    #         # # Tuner disabled
    #         # action_ecb._Callback__mappings[0].value = 3
    #         # self.assertEqual(action_ecb.enabled(action), True)

    #         # action_ecb._Callback__mappings[0].value = 0
    #         # self.assertEqual(action_ecb.enabled(action), True)


    # def test_show_tempo_with_ecb(self):
    #     display = DisplayLabel(layout = {
    #         "font": "foo"
    #     })

    #     ecb = MockEnabledCallback()

    #     with patch.dict(sys.modules, {
    #         "micropython": MockMicropython,
    #         "displayio": MockDisplayIO(),
    #         "adafruit_display_text": MockAdafruitDisplayText(),
    #         "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    #         "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    #         "adafruit_midi.program_change": MockAdafruitMIDIProgramChange(),
    #         "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
    #         "gc": MockGC()
    #     }):
    #         from lib.pyswitch.clients.kemper.mappings.tempo_bpm import MAPPING_TEMPO_BPM

    #         action = SHOW_TEMPO(
    #             display = display, 
    #             color = (4, 5, 6), 
    #             text = "foo",
    #             id = 67, 
    #             use_leds = True, 
    #             enable_callback = ecb
    #         )

    #         cb = action.callback
    #         self.assertIsInstance(cb, Callback)
    #         self.assertIsInstance(action, Action)

    #         self.assertEqual(cb._KemperShowTempoCallback__tempo_mapping, MAPPING_TEMPO_DISPLAY())
    #         self.assertEqual(cb._KemperShowTempoCallback__tuner_mapping, KemperMappings.TUNER_MODE_STATE())
    #         self.assertEqual(cb._KemperShowTempoCallback__bpm_mapping, MAPPING_TEMPO_BPM())
    #         self.assertEqual(cb._text, "foo")
    #         self.assertEqual(cb._color, (4, 5, 6))

    #         self.assertEqual(action.label, display)
    #         self.assertEqual(action.id, 67)
    #         self.assertEqual(action.uses_switch_leds, True)

    #         appl = MockController2()
    #         action.init(appl, None)

    #         # Must depend on tuner mode state
    #         # Tuner enabled
    #         # action_ecb._Callback__mappings[1].value = 1
    #         # self.assertEqual(action_ecb.enabled(action), False)

    #         # # Tuner disabled
    #         # action_ecb._Callback__mappings[1].value = 3
    #         # self.assertEqual(action_ecb.enabled(action), True)

    #         # action_ecb._Callback__mappings[1].value = 0
    #         # self.assertEqual(action_ecb.enabled(action), True)
