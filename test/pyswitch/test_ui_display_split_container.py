import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

with patch.dict(sys.modules, {
    "micropython": MockMicropython,
    "displayio": MockDisplayIO(),
    "adafruit_display_text": MockAdafruitDisplayText(),
    "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
    "usb_midi": MockUsbMidi(),
    "adafruit_midi": MockAdafruitMIDI(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "adafruit_midi.program_change": MockAdafruitMIDIProgramChange(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "gc": MockGC()
}):
    from lib.pyswitch.ui.ui import DisplayBounds, DisplayElement
    from lib.pyswitch.ui.elements import DisplaySplitContainer

    from .mocks_appl import *
    from .mocks_ui import *


###############################################################################################


class TestDisplaySplitContainer(unittest.TestCase):

    def test_split_horizontal(self):
        cont = DisplaySplitContainer(
            bounds = DisplayBounds(20, 30, 600, 500),
            direction = DisplaySplitContainer.HORIZONTAL
        )

        el_1 = DisplayElement()
        el_2 = DisplayElement()
        el_3 = DisplayElement()
        el_4 = DisplayElement()
        el_5 = DisplayElement()

        cont.add(el_1)
        self.assertEqual(el_1.bounds, DisplayBounds(20, 30, 600, 500))

        cont.add(el_2)
        self.assertEqual(el_1.bounds, DisplayBounds(20, 30, 300, 500))        
        self.assertEqual(el_2.bounds, DisplayBounds(320, 30, 300, 500))        

        cont.add(el_3)
        self.assertEqual(el_1.bounds, DisplayBounds(20, 30, 200, 500))        
        self.assertEqual(el_2.bounds, DisplayBounds(220, 30, 200, 500))        
        self.assertEqual(el_3.bounds, DisplayBounds(420, 30, 200, 500))        

        cont.set(el_4, 1)
        self.assertEqual(el_1.bounds, DisplayBounds(20, 30, 200, 500))        
        self.assertEqual(el_4.bounds, DisplayBounds(220, 30, 200, 500))        
        self.assertEqual(el_3.bounds, DisplayBounds(420, 30, 200, 500))        

        cont.set(el_5, 4)
        self.assertEqual(el_1.bounds, DisplayBounds(20, 30, 150, 500))        
        self.assertEqual(el_4.bounds, DisplayBounds(170, 30, 150, 500))        
        self.assertEqual(el_3.bounds, DisplayBounds(320, 30, 150, 500))        
        self.assertEqual(el_5.bounds, DisplayBounds(470, 30, 150, 500))        


    def test_split_vertical(self):
        cont = DisplaySplitContainer(
            bounds = DisplayBounds(20, 30, 500, 600),
            direction = DisplaySplitContainer.VERTICAL
        )

        el_1 = DisplayElement()
        el_2 = DisplayElement()
        el_3 = DisplayElement()
        el_4 = DisplayElement()
        el_5 = DisplayElement()

        cont.add(el_1)
        self.assertEqual(el_1.bounds, DisplayBounds(20, 30, 500, 600))

        cont.add(el_2)
        self.assertEqual(el_1.bounds, DisplayBounds(20, 30, 500, 300))        
        self.assertEqual(el_2.bounds, DisplayBounds(20, 330, 500, 300))        

        cont.add(el_3)
        self.assertEqual(el_1.bounds, DisplayBounds(20, 30, 500, 200))        
        self.assertEqual(el_2.bounds, DisplayBounds(20, 230, 500, 200))        
        self.assertEqual(el_3.bounds, DisplayBounds(20, 430, 500, 200))        

        cont.set(el_4, 1)
        self.assertEqual(el_1.bounds, DisplayBounds(20, 30, 500, 200))        
        self.assertEqual(el_4.bounds, DisplayBounds(20, 230, 500, 200))        
        self.assertEqual(el_3.bounds, DisplayBounds(20, 430, 500, 200))        

        cont.set(el_5, 4)
        self.assertEqual(el_1.bounds, DisplayBounds(20, 30, 500, 150))        
        self.assertEqual(el_4.bounds, DisplayBounds(20, 180, 500, 150))        
        self.assertEqual(el_3.bounds, DisplayBounds(20, 330, 500, 150))        
        self.assertEqual(el_5.bounds, DisplayBounds(20, 480, 500, 150))        
