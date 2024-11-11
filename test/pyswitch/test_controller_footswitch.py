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
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "gc": MockGC()
}):
    from .mocks_misc import MockMisc

    with patch.dict(sys.modules, {
        "lib.pyswitch.misc": MockMisc
    }):
        
        from lib.pyswitch.controller.FootSwitchController import FootSwitchController
        from lib.pyswitch.misc import Colors, Updater
        from .mocks_appl import *


class MockControllerReplacement(Updater):
    def __init__(self, config = {}, num_leds = 0):
        Updater.__init__(self)

        self.led_driver = MockNeoPixelDriver()
        self.led_driver.init(num_leds)
        self.config = config


##################################################################################################################################


class TestControllerFootswitch(unittest.TestCase):

    def test_minimal(self):
        appl = MockControllerReplacement()
        switch_1 = MockSwitch()

        fs = FootSwitchController(appl, {
            "assignment": {
                "model": switch_1
            },
        })

        self.assertEqual(fs.color, None)
        self.assertEqual(fs.brightness, None)

        self.assertEqual(fs.colors, [])
        self.assertEqual(fs.brightnesses, [])

    ##############################################################################

    def test_default_color_and_brightness(self):
        appl = MockControllerReplacement(num_leds=5)
        switch_1 = MockSwitch()

        fs = FootSwitchController(appl, {
            "assignment": {
                "model": switch_1,
                "pixels": (2, 4)
            }
        })

        self.assertEqual(fs.color, Colors.WHITE)
        self.assertEqual(fs.brightness, 0.5)

        for c in fs.colors:
            self.assertEqual(c, Colors.WHITE)

        self.assertEqual(len(fs.colors), 2)
        self.assertEqual(fs.brightnesses, [0.5, 0.5])

    ##############################################################################

    def test_set_color_and_brightness(self):
        appl = MockControllerReplacement(num_leds=5)
        switch_1 = MockSwitch()

        fs = FootSwitchController(appl, {
            "assignment": {
                "model": switch_1,
                "pixels": (0, 1, 2, 3, 4)
            }
        })

        # Set color
        fs.color = (4, 6, 5)

        self.assertEqual(fs.color, (4, 6, 5))
        self.assertEqual(fs.colors, [(4, 6, 5) for i in range(5)])

        fs.colors = [(1, 2, 3), (4, 5, 6), (7, 8, 9), (10, 11, 12), (13, 14, 15)]

        self.assertEqual(fs.color, (1, 2, 3))
        self.assertEqual(fs.colors, [(1, 2, 3), (4, 5, 6), (7, 8, 9), (10, 11, 12), (13, 14, 15)])
        
        # Brightnesses
        fs.color = (50, 100, 200)
        fs.brightness = 0.4
        
        self.assertEqual(fs.brightness, 0.4)
        self.assertEqual(fs.brightnesses, [0.4 for i in range(5)])

        self.assertEqual(appl.led_driver.leds, [(20, 40, 80) for i in range(5)])

        fs.brightnesses = [0, 0.1, 0.4, 1, 1]

        self.assertEqual(fs.brightness, 0)
        self.assertEqual(fs.brightnesses, [0, 0.1, 0.4, 1, 1])

        self.assertEqual(appl.led_driver.leds, [(0, 0, 0), (5, 10, 20), (20, 40, 80), (50, 100, 200), (50, 100, 200)])

##############################################################################

    def test_invalid_colors_and_brightnesses(self):
        appl = MockControllerReplacement(num_leds=5)
        switch_1 = MockSwitch()        

        fs = FootSwitchController(appl, {
            "assignment": {
                "model": switch_1,
                "pixels": (2, 4)
            }
        })

        with self.assertRaises(Exception):            
            fs.colors = [(0, 0, 0)]

        with self.assertRaises(Exception):            
            fs.colors = ((0, 0, 0), (0, 0, 0))

        with self.assertRaises(Exception):            
            fs.brightnesses = [1]

        
##############################################################################

    def test_no_pixels(self):
        appl = MockControllerReplacement(num_leds=5)
        switch_1 = MockSwitch()        

        fs = FootSwitchController(appl, {
            "assignment": {
                "model": switch_1
            }
        })

        fs.brightnesses = [0, 1]
        self.assertEqual(fs.brightnesses, [])

