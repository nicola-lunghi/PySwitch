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
    "displayio": MockDisplayIO(),
    "adafruit_display_text": MockAdafruitDisplayText(),
    "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
    "gc": MockGC()
}):
    from .mocks_callback import *

    from lib.pyswitch.controller.preview import ValuePreview
    from lib.pyswitch.ui.elements import DisplayLabel
    from .mocks_appl import *


##################################################################################################################################


class TestValuePreview(unittest.TestCase):

    def test_private_init(self):
        with self.assertRaises(Exception):
            ValuePreview(
                create_key = None, 
                label = None, 
                timeout_millis = 0, 
                blink_interval_millis = 0, 
                blink_color = None
            )

    def test_singleton(self):
        display1 = DisplayLabel(layout = {
            "font": "foo"
        })
        display2 = DisplayLabel(layout = {
            "font": "foo"
        })

        vp1 = ValuePreview.get(label = display1)
        vp2 = ValuePreview.get(label = display2)

        self.assertEqual(ValuePreview.get(label = display1), vp1)
        self.assertEqual(ValuePreview.get(label = display2), vp2)

        self.assertEqual(ValuePreview.get(label = display1), vp1)
        self.assertEqual(ValuePreview.get(label = display2), vp2)

    def test_clients(self):
        # display1 = DisplayLabel(layout = {
        #     "font": "foo"
        # })
        # display2 = DisplayLabel(layout = {
        #     "font": "foo"
        # })

        # vp1 = ValuePreview.get(label = display1)
            