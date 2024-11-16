import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

with patch.dict(sys.modules, {
    "micropython": MockMicropython,
    "displayio": MockDisplayIO(),
    "adafruit_display_text": MockAdafruitDisplayText(),
    "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "adafruit_midi.program_change": MockAdafruitMIDIProgramChange(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "gc": MockGC()
}):
    from lib.pyswitch.ui.UiController import UiController
    from lib.pyswitch.ui.elements import DisplayLabel, DisplaySplitContainer
    from lib.pyswitch.misc import Updater

    from .mocks_ui import *
    from .mocks_appl import *


class MockController2(Updater):
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

        appl = MockController2()
        ui.init(appl)

        ui.show()

        self.assertEqual(ui.current.font_loader, font_loader)
        self.assertEqual(ui.current, display)
        self.assertEqual(ui.bounds, DisplayBounds(0, 0, 300, 400))

        self.assertEqual(ui.current._initialized, True)
        self.assertEqual(display_driver.tft.show_calls, [ui.current.splash])

    
    def test_condition(self):
        period = MockPeriodCounter()

        display_driver = MockDisplayDriver(300, 400)
        display_driver.init()

        font_loader = MockFontLoader()

        element_yes = DisplayElement(id = "yes")
        element_no = DisplayElement(id = "no")

        condition_1 = MockCondition(
            yes = element_yes,
            no = element_no
        )
        ui = UiController(display_driver, font_loader, condition_1)

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            midi = MockMidiController(),
            period_counter = period,
            ui = ui
        )

        splashes = {
            "yes": None,
            "no": None
        }

        # Step 1
        def prep1():
            period.exceed_next_time = True
            condition_1.bool_value = False

            self.assertEqual(ui.current, element_yes)
            self.assertEqual(ui.current._initialized, True)
            splashes["yes"] = ui.current.splash

            self.assertEqual(display_driver.tft.show_calls, [splashes["yes"]])            

        def eval1():
            self.assertEqual(ui.current, element_no)
            self.assertEqual(ui.current._initialized, True)
            splashes["no"] = ui.current.splash

            self.assertEqual(display_driver.tft.show_calls, [splashes["yes"], splashes["no"]])

            return True
        
        # Step 2
        def prep2():
            period.exceed_next_time = True
            condition_1.bool_value = True
            appl.running = False

        def eval2():
            self.assertEqual(ui.current, element_yes)
            self.assertEqual(display_driver.tft.show_calls, [splashes["yes"], splashes["no"]])

            return True
        
        # Step 3
        def prep3():
            period.exceed_next_time = True            
            condition_1.bool_value = False
            appl.running = True

        def eval3():
            self.assertEqual(ui.current, element_no)            
            self.assertEqual(display_driver.tft.show_calls, [splashes["yes"], splashes["no"]])

            return True
        
        # Step 3
        def prep4():
            period.exceed_next_time = True            
            condition_1.bool_value = True

        def eval4():
            self.assertEqual(ui.current, element_yes)            
            self.assertEqual(display_driver.tft.show_calls, [splashes["yes"], splashes["no"], splashes["yes"]])

            return False

        # Build scenes hierarchy
        appl.next_step = SceneStep(
            num_pass_ticks = 5,
            prepare = prep1,
            evaluate = eval1,

            next = SceneStep(
                num_pass_ticks = 5,
                prepare = prep2,
                evaluate = eval2,

                next = SceneStep(
                    num_pass_ticks = 5,
                    prepare = prep3,
                    evaluate = eval3,

                    next = SceneStep(
                        num_pass_ticks = 5,
                        prepare = prep4,
                        evaluate = eval4
                    )
                )
            )
        )

        # Run process
        appl.process()


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
        appl = MockController2()
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


    def test_search(self):
        display_driver = MockDisplayDriver(300, 400)
        display_driver.init()

        element_1 = DisplayElement(id = 1)
        element_2 = DisplayElement(id = 2)
        element_3 = MockUpdateableDisplayElement(id = 3)

        display_yes = HierarchicalDisplayElement(
            id = "yess",
            children = [
                element_1,
                element_2,
                None,
                element_3
            ]
        )

        sub_1 = DisplayElement(id = "sub_1")
        sub_2 = DisplayElement(id = "sub_2")

        display_no = DisplaySplitContainer(
            id = "split",
            children = [
                sub_1,
                sub_2
            ]
        )

        condition_1 = MockCondition(
            yes = display_yes,
            no = display_no
        )

        font_loader = MockFontLoader()
        ui = UiController(display_driver, font_loader, root = condition_1)        
        appl = MockController2()
        ui.init(appl)

        self.assertEqual(ui.search(id = "yess"), display_yes)
        self.assertEqual(ui.search(id = 1), element_1)
        self.assertEqual(ui.search(id = 2), element_2)
        self.assertEqual(ui.search(id = 3), element_3)
        self.assertEqual(ui.search(id = 4), None)

        self.assertEqual(ui.search(id = "split"), display_no)
        self.assertEqual(ui.search(id = "sub_1"), sub_1)
        self.assertEqual(ui.search(id = "sub_2"), sub_2)

        self.assertEqual(ui.search(id = "split", index = -1), None)
        self.assertEqual(ui.search(id = "split", index = 0), sub_1)
        self.assertEqual(ui.search(id = "split", index = 1), sub_2)
        self.assertEqual(ui.search(id = "split", index = 2), None)


##########################################################################################################


    def test_error_no_root(self):
        display_driver = MockDisplayDriver(300, 400)
        display_driver.init()

        font_loader = MockFontLoader()

        ui = UiController(display_driver, font_loader)        

        appl = MockController2()

        with self.assertRaises(Exception):
            ui.init(appl)


    def test_error_set_root_after_init(self):
        display_driver = MockDisplayDriver(300, 400)
        display_driver.init()

        font_loader = MockFontLoader()

        element_1 = DisplayElement(id = 1)
        element_2 = DisplayElement(id = 2)

        ui = UiController(display_driver, font_loader, element_1)

        appl = MockController2()
        ui.init(appl)

        with self.assertRaises(Exception):
            ui.set_root(element_2)


    def test_error_show_before_init(self):
        display_driver = MockDisplayDriver(300, 400)
        display_driver.init()

        font_loader = MockFontLoader()

        element_1 = DisplayElement(id = 1)

        ui = UiController(display_driver, font_loader, element_1)

        with self.assertRaises(Exception):
            ui.show()


    def test_error_search_before_init(self):
        display_driver = MockDisplayDriver(300, 400)
        display_driver.init()

        font_loader = MockFontLoader()

        element_1 = DisplayElement(id = 1)

        ui = UiController(display_driver, font_loader, element_1)

        with self.assertRaises(Exception):
            ui.search({})


