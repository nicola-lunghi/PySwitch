import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

with patch.dict(sys.modules, {
    "displayio": MockDisplayIO(),
    "adafruit_display_text": MockAdafruitDisplayText(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "gc": MockGC()
}):
    from lib.pyswitch.ui.UiController import UiController
    from lib.pyswitch.ui.elements import DisplayLabel
    from lib.pyswitch.misc import Updater

    from .mocks_ui import *


class MockController(Updater):
    pass


#########################################################################


class TestUiController(unittest.TestCase):

    def test(self):
        display_driver = MockDisplayDriver(300, 400)
        display_driver.init()

        font_loader = MockFontLoader()

        ui = UiController(display_driver, font_loader)        

        display = DisplayElement(id = 1)
        ui.set_root(display)

        appl = MockController()
        ui.init(appl)

        ui.show()

        self.assertEqual(ui.current.font_loader, font_loader)
        self.assertEqual(ui.current.root, display)
        self.assertEqual(ui.bounds, DisplayBounds(0, 0, 300, 400))

        self.assertEqual(ui.current.root._initialized, True)
        self.assertEqual(display_driver.tft.show_calls, [ui.current.splash])


    def test_no_root(self):
        display_driver = MockDisplayDriver(300, 400)
        display_driver.init()

        font_loader = MockFontLoader()

        ui = UiController(display_driver, font_loader)        

        appl = MockController()

        with self.assertRaises(Exception):
            ui.init(appl)


    def test_add_updateables(self):
        display_driver = MockDisplayDriver(300, 400)
        display_driver.init()

        element_1 = DisplayElement(id = 1)
        element_2 = DisplayElement(id = 2)
        element_3 = MockUpdateableDisplayElement(id = 3)

        display = HierarchicalDisplayElement(
            children = [
                element_1,
                element_2,
                None,
                element_3
            ]
        )

        font_loader = MockFontLoader()
        ui = UiController(display_driver, font_loader, root = display)        
        appl = MockController()
        ui.init(appl)
        
        self.assertEqual(element_1._initialized, False)
        self.assertEqual(element_2._initialized, False)
        self.assertEqual(element_3._initialized, False)

        ui.show()

        self.assertEqual(element_1._initialized, True)
        self.assertEqual(element_2._initialized, True)
        self.assertEqual(element_3._initialized, True)

        appl.update()

        self.assertEqual(element_3.num_update_calls, 1)


    def test_create_label(self):
        display_driver = MockDisplayDriver()
        display_driver.init()

        font_loader = MockFontLoader()

        ui = UiController(display_driver, font_loader)

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
