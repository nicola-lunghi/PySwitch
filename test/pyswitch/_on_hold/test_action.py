import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

# Import subject under test
with patch.dict(sys.modules, {
    "displayio": MockDisplayIO(),
    "adafruit_display_text": MockAdafruitDisplayText(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "gc": MockGC()
}):
    from lib.pyswitch.controller.actions.Action import Action
    from .mocks_ui import *


class MockController:
    def __init__(self, config = {}, ui = None):
        self.config = config
        self.ui = ui


class MockFootSwitch:
    def __init__(self, id = ""):
        self.id = id
        self.actions = []
        self.pixels = []
        self.colors = []


class MockAction(Action):
    def __init__(self, config = {}, use_leds = False):
        super().__init__(config)

        self.uses_switch_leds = use_leds


#################################################################################


class TestAction(unittest.TestCase):

    def test_repr(self):
        appl = MockController()
        switch = MockFootSwitch(id = "foo")
        action = MockAction()

        self.assertTrue("MockAction" in repr(action))        

        action.init(appl, switch)

        self.assertTrue("MockAction" in repr(action))
        self.assertTrue("foo" in repr(action))

        self.assertTrue("MockAction" in action.id)
        self.assertTrue("foo" in action.id)


#################################################################################


    def test_led_segments_one_action(self):
        appl = MockController()
        switch = MockFootSwitch()
        
        action_1 = MockAction()
        action_2 = MockAction()
        action_3 = MockAction()
        action_4 = MockAction(use_leds = True)
        action_5 = MockAction()

        with self.assertRaises(Exception):           
            action_4._get_led_segments()

        action_1.init(appl, switch)
        action_2.init(appl, switch)
        action_3.init(appl, switch)
        action_4.init(appl, switch)
        action_5.init(appl, switch)

        ### 5 Actions
        switch.actions = [
            action_1,
            action_2,
            action_3,
            action_4,
            action_5
        ]

        # One pixel
        switch.pixels = [11]
        self.assertEqual(action_4._get_led_segments(), [0])

        with self.assertRaises(Exception):           
            action_1._get_led_segments()

        with self.assertRaises(Exception):           
            action_2._get_led_segments()

        with self.assertRaises(Exception):           
            action_3._get_led_segments()
        
        with self.assertRaises(Exception):           
            action_5._get_led_segments()

        # Two pixels
        switch.pixels = [11, 13]
        self.assertEqual(action_4._get_led_segments(), [0, 1])

        # Three pixels
        switch.pixels = [11, 13, 15]
        self.assertEqual(action_4._get_led_segments(), [0, 1, 2])

        # Four pixels
        switch.pixels = [11, 13, 15, 19]
        self.assertEqual(action_4._get_led_segments(), [0, 1, 2, 3])

        # Five pixels
        switch.pixels = [11, 13, 15, 19, 20]
        self.assertEqual(action_4._get_led_segments(), [0, 1, 2, 3, 4])

        # Six pixels
        switch.pixels = [11, 13, 15, 19, 20, 23]
        self.assertEqual(action_4._get_led_segments(), [0, 1, 2, 3, 4, 5])


#################################################################################


    def test_led_segments_three_actions(self):
        appl = MockController()
        switch = MockFootSwitch()
        
        action_1 = MockAction(use_leds = True)
        action_2 = MockAction(use_leds = True)
        action_3 = MockAction()
        action_4 = MockAction(use_leds = True)
        action_5 = MockAction()

        action_1.init(appl, switch)
        action_2.init(appl, switch)
        action_3.init(appl, switch)
        action_4.init(appl, switch)
        action_5.init(appl, switch)

        ### 5 Actions
        switch.actions = [
            action_1,
            action_2,
            action_3,
            action_4,
            action_5
        ]

        # One pixel
        switch.pixels = [11]
        self.assertEqual(action_1._get_led_segments(), [0])
        self.assertEqual(action_2._get_led_segments(), [])
        self.assertEqual(action_4._get_led_segments(), [])

        with self.assertRaises(Exception):           
            action_3._get_led_segments()
        
        with self.assertRaises(Exception):           
            action_5._get_led_segments()

        # Two pixels
        switch.pixels = [11, 13]
        self.assertEqual(action_1._get_led_segments(), [0])
        self.assertEqual(action_2._get_led_segments(), [1])
        self.assertEqual(action_4._get_led_segments(), [])

        # Three pixels
        switch.pixels = [11, 13, 15]
        self.assertEqual(action_1._get_led_segments(), [0])
        self.assertEqual(action_2._get_led_segments(), [1])
        self.assertEqual(action_4._get_led_segments(), [2])

        # Four pixels
        switch.pixels = [11, 13, 15, 19]
        self.assertEqual(action_1._get_led_segments(), [0, 1])
        self.assertEqual(action_2._get_led_segments(), [2])
        self.assertEqual(action_4._get_led_segments(), [3])

        # Five pixels
        switch.pixels = [11, 13, 15, 19, 20]
        self.assertEqual(action_1._get_led_segments(), [0, 1, 2])
        self.assertEqual(action_2._get_led_segments(), [3])
        self.assertEqual(action_4._get_led_segments(), [4])

        # Six pixels
        switch.pixels = [11, 13, 15, 19, 20, 23]
        self.assertEqual(action_1._get_led_segments(), [0, 1, 2, 3])
        self.assertEqual(action_2._get_led_segments(), [4])
        self.assertEqual(action_4._get_led_segments(), [5])

        # Disable action 1
        action_1.enabled = False
        self.assertEqual(action_1._get_led_segments(), [])
        self.assertEqual(action_2._get_led_segments(), [0, 1, 2, 3, 4])
        self.assertEqual(action_4._get_led_segments(), [5])

        # Disable action 2
        action_1.enabled = True
        action_2.enabled = False
        self.assertEqual(action_1._get_led_segments(), [0, 1, 2, 3, 4])
        self.assertEqual(action_2._get_led_segments(), [])
        self.assertEqual(action_4._get_led_segments(), [5])

        # No LED actions at all but action 1 but this is disabled        
        action_1.enabled = False
        action_2.uses_switch_leds = False
        action_4.uses_switch_leds = False
        self.assertEqual(action_1._get_led_segments(), [])
        

########################################################################################


    def test_label_not_found(self):
        ui = MockUserInterface()
        appl = MockController(ui = ui)
        switch = MockFootSwitch()
        action = MockAction({
            "display": {
                "id": "foo"
            }
        })

        with self.assertRaises(Exception):       
            action.init(appl, switch)


########################################################################################


    def test_label(self):
        ui = MockUserInterface()
        appl = MockController(ui = ui)
        switch = MockFootSwitch()
        action = MockAction({
            "display": {
                "id": "foo"
            }
        })

        label = DisplayElement(id = "foo")

        ui.root.add(
            label
        )

        action.init(appl, switch)

        self.assertEqual(action.label, label)


########################################################################################


    def test_label_existing_in_split_container(self):
        ui = MockUserInterface()
        appl = MockController(ui = ui)
        switch = MockFootSwitch()
        action = MockAction({
            "display": {
                "id": "foo",
                "index": 1
            }
        })

        label_1 = DisplayElement(id = "child1")
        label_2 = DisplayElement(id = "child2")

        container = MockHierarchicalDisplayElement(id = "foo")
        container.add(label_1)
        container.add(label_2)

        ui.root.add(
            container
        )

        action.init(appl, switch)

        self.assertEqual(action.label, label_2)


########################################################################################


    def test_label_new_in_split_container(self):
        ui = MockUserInterface()
        appl = MockController(ui = ui)
        switch = MockFootSwitch()
        action = MockAction({
            "display": {
                "id": "foo",
                "index": 1,
                "layout": {
                    "font": "foofont",
                    "backColor": (2, 3, 4),
                    "stroke": 3
                }
            }
        })

        container = MockHierarchicalDisplayElement(id = "foo")

        ui.root.add(
            container
        )

        action.init(appl, switch)

        self.assertEqual(action.label, ui.root.child(0).child(1))
        self.assertEqual(action.label.layout["font"], "foofont")
        self.assertEqual(action.label.layout["backColor"],(2, 3, 4))
        self.assertEqual(action.label.layout["stroke"], 3)


########################################################################################


    def test_property_enabled(self):
        appl = MockController()
        switch = MockFootSwitch()
        action = MockAction({
            "enabled": False
        })

        action.init(appl, switch)

        self.assertEqual(action.enabled, False)

        action.enabled = False
        self.assertEqual(action.enabled, False)

        action.enabled = True
        self.assertEqual(action.enabled, True)


########################################################################################


    def test_property_enabled_default(self):
        appl = MockController()
        switch = MockFootSwitch()
        action = MockAction()

        action.init(appl, switch)

        self.assertEqual(action.enabled, True)


########################################################################################


    def test_property_set_switch_colors_brightness(self):
        appl = MockController()
        switch = MockFootSwitch()
        
        action_1 = MockAction()
        action_2 = MockAction(use_leds = True)
        action_3 = MockAction()
        action_4 = MockAction(use_leds = True)
        action_5 = MockAction(use_leds = True)

        action_1.init(appl, switch)
        action_2.init(appl, switch)
        action_3.init(appl, switch)
        action_4.init(appl, switch)
        action_5.init(appl, switch)

        ### 5 Actions
        switch.actions = [
            action_1,
            action_2,
            action_3,
            action_4,
            action_5
        ]

        # One pixel
        switch.pixels = [11]
        switch.colors = [(0, 0, 0)]
        switch.brightnesses = [0]

        action_2.switch_color = (2, 3, 4)
        action_2.switch_brightness = 1

        self.assertEqual(switch.colors, [(2, 3, 4)])
        self.assertEqual(switch.brightnesses, [1])
        self.assertEqual(action_2.switch_brightness, 1)

        # Two pixels
        switch.pixels = [11, 12]
        switch.colors = [(0, 0, 0), (0, 0, 0)]
        switch.brightnesses = [0, 0]

        action_2.switch_color = (2, 30, 4)
        action_4.switch_color = (2, 30, 40)
        action_5.switch_color = (2, 30, 400)
        action_2.switch_brightness = 0.2
        action_4.switch_brightness = 0.3
        action_5.switch_brightness = 0.4
        
        self.assertEqual(switch.colors, [(2, 30, 4), (2, 30, 40)])
        self.assertEqual(switch.brightnesses, [0.2, 0.3])
        
        self.assertEqual(action_2.switch_brightness, 0.2)
        self.assertEqual(action_4.switch_brightness, 0.3)
        self.assertEqual(action_5.switch_brightness, None)

        # Three pixels
        switch.pixels = [11, 12, 34]
        switch.colors = [(0, 0, 0), (0, 0, 0), (0, 0, 0)]
        switch.brightnesses = [0, 0, 0]

        action_2.switch_color = (2, 30, 4)
        action_4.switch_color = (2, 30, 40)
        action_5.switch_color = (2, 30, 400)
        action_2.switch_brightness = 0.2
        action_4.switch_brightness = 0.3
        action_5.switch_brightness = 0.4
        
        self.assertEqual(switch.colors, [(2, 30, 4), (2, 30, 40), (2, 30, 400)])
        self.assertEqual(switch.brightnesses, [0.2, 0.3, 0.4])

        self.assertEqual(action_2.switch_brightness, 0.2)
        self.assertEqual(action_4.switch_brightness, 0.3)
        self.assertEqual(action_5.switch_brightness, 0.4)


########################################################################################


    def test_property_set_switch_color_brightness_tuples(self):
        appl = MockController()
        switch = MockFootSwitch()
        
        action_1 = MockAction()
        action_2 = MockAction(use_leds = True)
        action_3 = MockAction()
        action_4 = MockAction(use_leds = True)
        action_5 = MockAction(use_leds = True)

        action_1.init(appl, switch)
        action_2.init(appl, switch)
        action_3.init(appl, switch)
        action_4.init(appl, switch)
        action_5.init(appl, switch)

        ### 5 Actions
        switch.actions = [
            action_1,
            action_2,
            action_3,
            action_4,
            action_5
        ]

        # One pixel
        switch.pixels = [11]
        switch.colors = [(0, 0, 0)]
        switch.brightnesses = [0]

        action_2.switch_color = [(2, 3, 4), (3, 4, 5)]
        action_2.switch_brightness = 0.2
        
        self.assertEqual(switch.colors, [(3, 4, 5)])
        self.assertEqual(switch.brightnesses, [0.2])

        # Two pixels
        switch.pixels = [11, 12]
        switch.colors = [(0, 0, 0), (0, 0, 0)]
        switch.brightnesses = [0, 0]

        action_2.switch_color = [(2, 3, 4), (3, 4, 5)]
        action_4.switch_color = [(2, 30, 40), (3, 40, 5)]
        action_5.switch_color = [(2, 3, 400), (3, 4, 5)]
        action_2.switch_brightness = 0.2
        action_4.switch_brightness = 0.4
        action_5.switch_brightness = 0.6

        self.assertEqual(switch.colors, [(3, 4, 5), (3, 40, 5)])
        self.assertEqual(switch.brightnesses, [0.2, 0.4])

        # Three pixels
        switch.pixels = [11, 12, 34]
        switch.colors = [(0, 0, 0), (0, 0, 0), (0, 0, 0)]
        switch.brightnesses = [0, 0, 0]

        action_2.switch_color = [(2, 3, 4), (3, 4, 5)]
        action_4.switch_color = [(2, 30, 40), (30, 4, 5)]
        action_5.switch_color = [(2, 30, 400), (31, 4, 5)]

        action_2.switch_brightness = 0.2
        action_4.switch_brightness = 0.4
        action_5.switch_brightness = 0.6

        self.assertEqual(switch.colors, [(3, 4, 5), (30, 4, 5), (31, 4, 5)])
        self.assertEqual(switch.brightnesses, [0.2, 0.4, 0.6])

        ### Only action 2 is enabled ##############################################
        action_4.enabled = False
        action_5.enabled = False

        # One pixel
        switch.pixels = [11]
        switch.colors = [(0, 0, 0)]
        switch.brightnesses = [0]

        action_2.switch_color = [(2, 3, 4), (3, 4, 5)]
        action_2.switch_brightness = 0.2

        self.assertEqual(switch.colors, [(3, 4, 5)])
        self.assertEqual(switch.brightnesses, [0.2])

        # Two pixels
        switch.pixels = [11, 12]
        switch.colors = [(0, 0, 0), (0, 0, 0)]
        switch.brightnesses = [0, 0]

        action_2.switch_color = [(2, 3, 4), (3, 4, 5)]
        action_4.switch_color = [(2, 30, 40), (3, 4, 5)]
        action_5.switch_color = [(2, 3, 400), (3, 4, 5)]

        action_2.switch_brightness = 0.2
        action_4.switch_brightness = 0.4
        action_5.switch_brightness = 0.6

        self.assertEqual(switch.colors, [(2, 3, 4), (3, 4, 5)])
        self.assertEqual(switch.brightnesses, [0.2, 0.2])

        # Three pixels
        switch.pixels = [11, 12, 34]
        switch.colors = [(0, 0, 0), (0, 0, 0), (0, 0, 0)]
        switch.brightnesses = [0, 0, 0]

        action_2.switch_color = [(2, 3, 4), (3, 4, 5), (6, 7, 8)]
        action_4.switch_color = [(2, 30, 40), (3, 4, 5), (4, 5, 78)]
        action_5.switch_color = [(2, 30, 400), (3, 4, 5), (2, 34, 56)]

        action_2.switch_brightness = 0.2
        action_4.switch_brightness = 0.4
        action_5.switch_brightness = 0.6

        self.assertEqual(switch.colors, [(2, 3, 4), (3, 4, 5), (6, 7, 8)])
        self.assertEqual(switch.brightnesses, [0.2, 0.2, 0.2])