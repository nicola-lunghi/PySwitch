import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

# Import subject under test
with patch.dict(sys.modules, {
    "micropython": MockMicropython,
    "displayio": MockDisplayIO(),
    "adafruit_display_text": MockAdafruitDisplayText(),
    #"adafruit_midi": MockAdafruitMIDI(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "adafruit_midi.program_change": MockAdafruitMIDIProgramChange(),
    "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
    "gc": MockGC()
}):
    from pyswitch.clients.kemper.callbacks.tempo_bpm import KemperTempoDisplayCallback
    from pyswitch.clients.kemper.mappings.tempo_bpm import MAPPING_TEMPO_BPM
    
    from pyswitch.ui.elements import DisplayLabel
    from .mocks_appl import *
    from .mocks_ui import MockUiController
          

class TestKemperBpmDisplayCallback(unittest.TestCase):

    def test(self):
        cb = KemperTempoDisplayCallback()

        self.assertIn(MAPPING_TEMPO_BPM(), cb._Callback__mappings)
        mapping = cb._Callback__mappings[0]

        label = DisplayLabel(
            layout = {
                "font": "foo"
            },
            callback = cb
        )

        appl = MockController()
        ui = MockUiController()
        label.init(ui, appl)

        cb.update_label(label)
        
        self.assertEqual(label.text, "")

        # Set a value
        mapping.value = 133 * 64

        cb.update_label(label)

        self.assertEqual(label.text, "133 bpm")
        
        # Set another value
        mapping.value = 155 * 64 + 1 # Must be rounded away

        cb.update_label(label)

        self.assertEqual(label.text, "155 bpm")

        # 16383 is assigned to 256 manually
        mapping.value = 16383

        cb.update_label(label)

        self.assertEqual(label.text, "256 bpm")
        
        mapping.value = 16382

        cb.update_label(label)

        self.assertEqual(label.text, "256 bpm")
        
        mapping.value = 16320

        cb.update_label(label)

        self.assertEqual(label.text, "255 bpm")
        




