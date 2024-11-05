import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

with patch.dict(sys.modules, {
    "displayio": MockDisplayIO(),
    "adafruit_display_text": MockAdafruitDisplayText(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "gc": MockGC()
}):
    from lib.pyswitch.ui.UserInterface import UserInterface
    from lib.pyswitch.ui.elements.elements import DisplayLabel

    from .mocks_ui import *


class MockST7789:
    def __init__(self):
        self.show_calls = []
        self.rootgroup = None

    def show(self, splash):
        self.show_calls.append({
            "splash": splash
        })


class MockDisplayDriver:
    def __init__(self, w = 0, h = 0):
        self.tft = None
        self.width = w
        self.height = h

    def init(self):
        self.tft = MockST7789()



class MockController:
    pass



#########################################################################


class TestUserInterface(unittest.TestCase):

    def test(self):
        display = MockDisplayDriver(300, 400)
        display.init()

        font_loader = MockFontLoader()

        ui = UserInterface(display, font_loader)
        
        self.assertIsInstance(ui.root, HierarchicalDisplayElement)
        self.assertEqual(ui.root.bounds, DisplayBounds(0, 0, 300, 400))
        self.assertEqual(ui.font_loader, font_loader)
        self.assertEqual(display.tft.rootgroup, ui.splash)

        self.assertEqual(ui.root._initialized, False)

        appl = MockController()

        ui.show(appl)

        self.assertEqual(ui.root._initialized, True)
        self.assertEqual(display.tft.show_calls, [{ "splash": ui.splash }])


    def test_create_label(self):
        display = MockDisplayDriver()
        display.init()

        font_loader = MockFontLoader()

        ui = UserInterface(display, font_loader)

        label = ui.create_label(
            bounds = DisplayBounds(20, 21, 34, 56),
            layout = {
                "font": "foo"
            },
            name = "fooname",
            id = 345
        )

        self.assertIsInstance(label, DisplayLabel)
        
        self.assertEqual(label.bounds, DisplayBounds(20, 21, 34, 56))
        self.assertEqual(label.name, "fooname")
        self.assertEqual(label.id, 345)
