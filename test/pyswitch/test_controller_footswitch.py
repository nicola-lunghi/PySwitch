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
    "gc": MockGC()
}):
    from .mocks_misc import MockMisc

    with patch.dict(sys.modules, {
        "lib.pyswitch.misc": MockMisc()
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

    def test_initial_color_and_brightness(self):
        appl = MockControllerReplacement(num_leds=5)
        switch_1 = MockSwitch()

        fs = FootSwitchController(appl, {
            "assignment": {
                "model": switch_1,
                "pixels": (2, 4)
            },
            "initialColors": [(2, 2, 2), (3, 3, 3)],
            "initialBrightness": 0.345
        })

        self.assertEqual(fs.color, (2, 2, 2))
        self.assertEqual(fs.brightness, 0.345)

        self.assertEqual(fs.colors, [(2, 2, 2), (3, 3, 3)])
        self.assertEqual(fs.brightnesses, [0.345, 0.345])

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

        available_colors = (Colors.GREEN, Colors.YELLOW, Colors.RED)
        
        self.assertEqual(fs.color in available_colors, True)
        self.assertEqual(fs.brightness, 1)

        for c in fs.colors:
            self.assertEqual(c  in available_colors, True)

        self.assertEqual(len(fs.colors), 2)
        self.assertEqual(fs.brightnesses, [1, 1])

    ##############################################################################

    def test_set_color_and_brightness(self):
        appl = MockControllerReplacement(num_leds=5)
        switch_1 = MockSwitch()

        fs = FootSwitchController(appl, {
            "assignment": {
                "model": switch_1,
                "pixels": (0, 1, 2, 3, 4)
            },
            "initialColors": [(1, 1, 1) for i in range(5)],
        })

        self.assertEqual(len(fs.colors), 5)
        self.assertEqual(fs.brightnesses, [1, 1, 1, 1, 1])

        # Set color
        fs.color = (4, 6, 5)

        self.assertEqual(fs.color, (4, 6, 5))
        self.assertEqual(fs.colors, [(4, 6, 5) for i in range(5)])

        fs.colors = [(1, 2, 3), (4, 5, 6), (7, 8, 9), (10, 11, 12), (13, 14, 15)]

        self.assertEqual(fs.color, (1, 2, 3))
        self.assertEqual(fs.colors, [(1, 2, 3), (4, 5, 6), (7, 8, 9), (10, 11, 12), (13, 14, 15)])
        
        self.assertEqual(appl.led_driver.leds, [(1, 1, 1) for i in range(5)])

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

        with self.assertRaises(Exception):            
            fs.brightnesses = (1, 1)

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

##############################################################################

    def test_debug(self):
        MockMisc.Tools.reset()

        appl = MockControllerReplacement(num_leds=1)
        switch_1 = MockSwitch()
        action_1 = MockAction()
        action_2 = MockAction()

        appl.config["debugSwitches"] = True

        fs = FootSwitchController(appl, {
            "assignment": {
                "model": switch_1,
                "pixels": [0]
            },
            "actions": [
                action_1,
                action_2,
            ]
        })

        start_msgs = len(MockMisc.Tools.msgs)

        # Color
        fs.color = (2, 3, 4)
        self.assertEqual(len(MockMisc.Tools.msgs), start_msgs + 1)

        fs.color = (2, 3, 4)
        self.assertEqual(len(MockMisc.Tools.msgs), start_msgs + 2)

        fs.colors = [(2, 3, 4)]
        self.assertEqual(len(MockMisc.Tools.msgs), start_msgs + 3)

        fs.colors = [(2, 3, 5)]
        self.assertEqual(len(MockMisc.Tools.msgs), start_msgs + 4)

        # Brightness
        fs.brightness = 0.5
        self.assertEqual(len(MockMisc.Tools.msgs), start_msgs + 5)

        fs.brightness = 0.5
        self.assertEqual(len(MockMisc.Tools.msgs), start_msgs + 6)

        fs.brightness = 0.6
        self.assertEqual(len(MockMisc.Tools.msgs), start_msgs + 7)

        fs.brightnesses = [0.7]
        self.assertEqual(len(MockMisc.Tools.msgs), start_msgs + 8)

        fs.brightnesses = [0.7]
        self.assertEqual(len(MockMisc.Tools.msgs), start_msgs + 9)

        fs.brightnesses = [0.70001]
        self.assertEqual(len(MockMisc.Tools.msgs), start_msgs + 10)

        # Push and release
        fs.process()
        self.assertEqual(len(MockMisc.Tools.msgs), start_msgs + 10)

        switch_1.shall_be_pushed = True
        fs.process()
        self.assertEqual(len(MockMisc.Tools.msgs), start_msgs + 12)

        fs.process()
        self.assertEqual(len(MockMisc.Tools.msgs), start_msgs + 12)

        switch_1.shall_be_pushed = False
        fs.process()
        self.assertEqual(len(MockMisc.Tools.msgs), start_msgs + 14)

        switch_1.shall_be_pushed = True
        action_2.enabled = False
        fs.process()
        self.assertEqual(len(MockMisc.Tools.msgs), start_msgs + 15)

        switch_1.shall_be_pushed = False
        fs.process()
        self.assertEqual(len(MockMisc.Tools.msgs), start_msgs + 16)
