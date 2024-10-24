import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

# Import subject under test
with patch.dict(sys.modules, {
    "displayio": MockDisplayIO(),
    "adafruit_display_text": MockAdafruitDisplayText(),
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

        from .mocks_appl import *
        from .mocks_ui import *
        from lib.pyswitch.controller.ExploreModeController import ExploreModeController
        from lib.pyswitch.misc import Colors


class MockSwitchFactory:
    def __init__(self):
        self.switches = []

    def create_switch(self, port):
        switch = MockSwitch(port)
        if port == "MockPort_23":
            switch.raise_on_init = ValueError()
        else:
            self.switches.append(switch)
        return switch
    
    def find_by_port(self, port):    # pragma: no cover
        for switch in self.switches:
            if switch.port != port:
                continue
            return switch
        return None          
    

class MockExploreModeController(ExploreModeController):
    def __init__(self, board, switch_factory, led_driver = None, ui = None, num_pixels_per_switch = 3, num_port_columns = 5):
        super().__init__(board, switch_factory, led_driver, ui, num_pixels_per_switch, num_port_columns)

        self._next_step = None

    def tick(self):
        if not self._next_step:  # pragma: no cover
            return super().tick()
        
        if callable(self._next_step.prepare):
            self._next_step.prepare()

        res = super().tick()
        if not res:  # pragma: no cover
            raise Exception("tick() does not return True")
        
        if not callable(self._next_step.evaluate):  # pragma: no cover
            return False
        
        ret = self._next_step.evaluate()

        self._next_step = self._next_step.next

        return ret        
    
    @property
    def next_step(self):  # pragma: no cover
        return self._next_step
    
    @next_step.setter
    def next_step(self, step):
        if not isinstance(step, SceneStep):  # pragma: no cover
            raise Exception("Invalid test step")
        
        self._next_step = step


##################################################################################################


class TestExploreMode(unittest.TestCase):

    def test_minimal(self):
        appl = MockExploreModeController(MockBoard(), MockSwitchFactory())    # Must not throw
    
        def eval1():
            return False

        # Build scenes hierarchy
        appl.next_step = SceneStep(
            evaluate = eval1
        )

        # Run process
        appl.process()


##################################################################################################


    def test_console_gpio_detect(self):
        MockMisc.Tools.reset()
        led_driver = MockNeoPixelDriver()
        switch_factory = MockSwitchFactory()

        appl = MockExploreModeController(
            board = MockBoard(), 
            switch_factory = switch_factory,
            led_driver = led_driver,
            num_pixels_per_switch = 2
        )

        self.assertIn("EXPLORE MODE", MockMisc.Tools.msgs_str)
        self.assertIn("GP4", MockMisc.Tools.msgs_str)
        self.assertIn("GP6", MockMisc.Tools.msgs_str)
        self.assertIn("GP11", MockMisc.Tools.msgs_str)
        self.assertNotIn("Error", MockMisc.Tools.msgs_str)

        self.assertEqual(len(appl.switches), 3)
        
        # Build scenario
        def prep1():
            switch_factory.find_by_port("MockPort_6").shall_be_pushed = True
            MockMisc.Tools.reset()

        def eval1():
            self.assertNotIn("GP4", MockMisc.Tools.msgs_str)
            self.assertIn("GP6", MockMisc.Tools.msgs_str)
            self.assertNotIn("GP11", MockMisc.Tools.msgs_str)
            return True

        def prep2():
            switch_factory.find_by_port("MockPort_6").shall_be_pushed = False
            switch_factory.find_by_port("MockPort_11").shall_be_pushed = True
            MockMisc.Tools.reset()

        def eval2():
            self.assertNotIn("GP4", MockMisc.Tools.msgs_str)
            self.assertNotIn("GP6", MockMisc.Tools.msgs_str)
            self.assertIn("GP11", MockMisc.Tools.msgs_str)            
            return False

        # Build scenes hierarchy
        appl.next_step = SceneStep(
            prepare = prep1,
            evaluate = eval1,

            next = SceneStep(
                prepare = prep2,
                evaluate = eval2
            )
        )

        # Run process
        appl.process()


##################################################################################################


    def test_ui_gpio_detect_5rows(self):
        MockMisc.Tools.reset()
        led_driver = MockNeoPixelDriver()
        switch_factory = MockSwitchFactory()
        ui = MockUserInterface(width = 999, height = 600)

        appl = MockExploreModeController(
            board = MockBoard(), 
            switch_factory = switch_factory,
            led_driver = led_driver,
            num_pixels_per_switch = 2,
            ui = ui
        )

        self.assertNotIn("EXPLORE MODE", MockMisc.Tools.msgs_str)
        self.assertNotIn("GP4", MockMisc.Tools.msgs_str)
        self.assertNotIn("GP6", MockMisc.Tools.msgs_str)
        self.assertNotIn("GP11", MockMisc.Tools.msgs_str)
        self.assertNotIn("Error", MockMisc.Tools.msgs_str)

        self.assertEqual(len(appl.switches), 3)
        self.assertEqual(len(ui.root.children), 2)
        self.assertEqual(len(ui.root.child(1).children), 1)
        self.assertEqual(len(ui.root.child(1).child(0).children), 3)
        
        label_0 = ui.root.child(1).child(0).child(0)
        label_1 = ui.root.child(1).child(0).child(1)
        label_2 = ui.root.child(1).child(0).child(2)

        self.assertEqual(label_0.bounds, DisplayBounds(0, 0, 333, 560))
        self.assertEqual(label_1.bounds, DisplayBounds(333, 0, 333, 560))
        self.assertEqual(label_2.bounds, DisplayBounds(666, 0, 333, 560))

        self.assertEqual(label_0.text, "GP11")
        self.assertEqual(label_1.text, "GP4")
        self.assertEqual(label_2.text, "GP6")

        # Build scenario
        def prep1():
            switch_factory.find_by_port("MockPort_6").shall_be_pushed = True
            MockMisc.Tools.reset()

        def eval1():
            self.assertNotIn("GP4", MockMisc.Tools.msgs_str)
            self.assertIn("GP6", MockMisc.Tools.msgs_str)
            self.assertNotIn("GP11", MockMisc.Tools.msgs_str)

            self.assertEqual(label_0.back_color, Colors.DARK_BLUE)
            self.assertEqual(label_1.back_color, Colors.DARK_BLUE)
            self.assertEqual(label_2.back_color, Colors.RED)
            return True

        def prep2():
            switch_factory.find_by_port("MockPort_6").shall_be_pushed = False
            switch_factory.find_by_port("MockPort_11").shall_be_pushed = True
            MockMisc.Tools.reset()

        def eval2():
            self.assertNotIn("GP4", MockMisc.Tools.msgs_str)
            self.assertNotIn("GP6", MockMisc.Tools.msgs_str)
            self.assertIn("GP11", MockMisc.Tools.msgs_str)            

            self.assertEqual(label_0.back_color, Colors.RED)
            self.assertEqual(label_1.back_color, Colors.DARK_BLUE)
            self.assertEqual(label_2.back_color, Colors.DARK_BLUE)
            return False

        # Build scenes hierarchy
        appl.next_step = SceneStep(
            prepare = prep1,
            evaluate = eval1,

            next = SceneStep(
                prepare = prep2,
                evaluate = eval2
            )
        )

        with patch.dict(sys.modules, {
            "adafruit_display_shapes.roundrect": MockDisplayShapes().roundrect(),
            "adafruit_display_shapes.rect": MockDisplayShapes().rect()
        }):
            # Run process
            appl.process()


##################################################################################################


    def test_ui_gpio_detect_2rows(self):
        MockMisc.Tools.reset()
        ui = MockUserInterface(width = 1000, height = 600)

        appl = MockExploreModeController(
            board = MockBoard(), 
            switch_factory = MockSwitchFactory(),
            led_driver = MockNeoPixelDriver(),
            num_pixels_per_switch = 2,
            ui = ui,
            num_port_columns = 2
        )

        self.assertEqual(len(appl.switches), 3)
        self.assertEqual(len(ui.root.children), 2)
        self.assertEqual(len(ui.root.child(1).children), 2)
        self.assertEqual(len(ui.root.child(1).child(0).children), 2)
        self.assertEqual(len(ui.root.child(1).child(1).children), 1)
        
        label_0 = ui.root.child(1).child(0).child(0)
        label_1 = ui.root.child(1).child(0).child(1)
        label_2 = ui.root.child(1).child(1).child(0)

        self.assertEqual(label_0.bounds, DisplayBounds(0, 0, 500, 280))
        self.assertEqual(label_1.bounds, DisplayBounds(500, 0, 500, 280))
        self.assertEqual(label_2.bounds, DisplayBounds(0, 280, 1000, 280))

        self.assertEqual(label_0.text, "GP11")
        self.assertEqual(label_1.text, "GP4")
        self.assertEqual(label_2.text, "GP6")


##################################################################################################


    def test_console_pixel_scan(self):
        self._test_console_pixel_scan(0, "up")
        self._test_console_pixel_scan(1, "down")
        self._test_console_pixel_scan(2, "up")

    def _test_console_pixel_scan(self, switch_id, direction):
        MockMisc.Tools.reset()
        led_driver = MockNeoPixelDriver()
        switch_factory = MockSwitchFactory()

        appl = MockExploreModeController(
            board = MockBoard(), 
            switch_factory = switch_factory,
            led_driver = led_driver,
            num_pixels_per_switch = 4
        )

        self.assertEqual(len(appl.switches), 3)
        
        # Build scenario
        def prep1():
            switch_factory.switches[switch_id].shall_be_pushed = True
            MockMisc.Tools.reset()
            pass

        def eval1():
            if direction == "up":
                self.assertIn("(0, 1, 2, 3) of 12", MockMisc.Tools.msgs_str)            
                self._assert_enlightened(led_driver, (0, 1, 2, 3))
            else:
                self.assertIn("(8, 9, 10, 11) of 12", MockMisc.Tools.msgs_str)
                self._assert_enlightened(led_driver, (8, 9, 10, 11))
            return True

        def prep2():
            switch_factory.switches[switch_id].shall_be_pushed = False

        def eval2():            
            return True

        def prep3():
            switch_factory.switches[switch_id].shall_be_pushed = True
            MockMisc.Tools.reset()            

        def eval3():
            self.assertIn("(4, 5, 6, 7) of 12", MockMisc.Tools.msgs_str)    
            self._assert_enlightened(led_driver, (4, 5, 6, 7))        
            return True
        
        def prep4():
            switch_factory.switches[switch_id].shall_be_pushed = False

        def eval4():            
            return True

        def prep5():
            switch_factory.switches[switch_id].shall_be_pushed = True
            MockMisc.Tools.reset()
            pass

        def eval5():
            if direction == "up":
                self.assertIn("(8, 9, 10, 11) of 12", MockMisc.Tools.msgs_str)
                self._assert_enlightened(led_driver, (8, 9, 10, 11))
            else:
                self.assertIn("(0, 1, 2, 3) of 12", MockMisc.Tools.msgs_str)     
                self._assert_enlightened(led_driver, (0, 1, 2, 3))       
            return True
        
        def prep6():
            switch_factory.switches[switch_id].shall_be_pushed = False

        def eval6():            
            return True

        def prep7():
            switch_factory.switches[switch_id].shall_be_pushed = True
            MockMisc.Tools.reset()
            pass

        def eval7():
            if direction == "up":
                self.assertIn("(0, 1, 2, 3) of 12", MockMisc.Tools.msgs_str)     
                self._assert_enlightened(led_driver, (0, 1, 2, 3))       
            else:
                self.assertIn("(8, 9, 10, 11) of 12", MockMisc.Tools.msgs_str)
                self._assert_enlightened(led_driver, (8, 9, 10, 11))                
            return False
        

        # Build scenes hierarchy
        appl.next_step = SceneStep(
            prepare = prep1,
            evaluate = eval1,

            next = SceneStep(
                prepare = prep2,
                evaluate = eval2,

                next = SceneStep(
                    prepare = prep3,
                    evaluate = eval3,

                    next = SceneStep(
                        prepare = prep4,
                        evaluate = eval4,

                        next = SceneStep(
                            prepare = prep5,
                            evaluate = eval5,

                            next = SceneStep(
                                prepare = prep6,
                                evaluate = eval6,

                                next = SceneStep(
                                    prepare = prep7,
                                    evaluate = eval7
                                )
                            )
                        )
                    )
                )
            )
        )

        # Run process
        appl.process()


##################################################################################################


    def test_ui_pixel_scan(self):
        self._test_ui_pixel_scan(0, "up")
        self._test_ui_pixel_scan(1, "down")
        self._test_ui_pixel_scan(2, "up")

    def _test_ui_pixel_scan(self, switch_id, direction):
        MockMisc.Tools.reset()
        led_driver = MockNeoPixelDriver()
        switch_factory = MockSwitchFactory()
        ui = MockUserInterface()

        appl = MockExploreModeController(
            board = MockBoard(), 
            switch_factory = switch_factory,
            led_driver = led_driver,
            num_pixels_per_switch = 3,
            ui = ui
        )

        self.assertEqual(len(appl.switches), 3)        
        self.assertEqual(len(ui.root.children), 2)

        label = ui.root.child(0)

        # Build scenario
        def prep1():
            switch_factory.switches[switch_id].shall_be_pushed = True
            MockMisc.Tools.reset()
            pass

        def eval1():
            if direction == "up":
                self.assertIn("(0, 1, 2) of 9", MockMisc.Tools.msgs_str)            
                self._assert_enlightened(led_driver, (0, 1, 2))
                self.assertIn("(0, 1, 2) of 9", label.text)
            else:
                self.assertIn("(6, 7, 8) of 9", MockMisc.Tools.msgs_str)
                self._assert_enlightened(led_driver, (6, 7, 8))
                self.assertIn("(6, 7, 8) of 9", label.text)
            return True

        def prep2():
            switch_factory.switches[switch_id].shall_be_pushed = False

        def eval2():            
            return True

        def prep3():
            switch_factory.switches[switch_id].shall_be_pushed = True
            MockMisc.Tools.reset()            

        def eval3():
            self.assertIn("(3, 4, 5) of 9", MockMisc.Tools.msgs_str)    
            self._assert_enlightened(led_driver, (3, 4, 5))        
            self.assertIn("(3, 4, 5) of 9", label.text)
            return True
        
        def prep4():
            switch_factory.switches[switch_id].shall_be_pushed = False

        def eval4():            
            return True

        def prep5():
            switch_factory.switches[switch_id].shall_be_pushed = True
            MockMisc.Tools.reset()
            pass

        def eval5():
            if direction == "up":
                self.assertIn("(6, 7, 8) of 9", MockMisc.Tools.msgs_str)
                self._assert_enlightened(led_driver, (6, 7, 8))
                self.assertIn("(6, 7, 8) of 9", label.text)
            else:
                self.assertIn("(0, 1, 2) of 9", MockMisc.Tools.msgs_str)     
                self._assert_enlightened(led_driver, (0, 1, 2))  
                self.assertIn("(0, 1, 2) of 9", label.text)     
            return False
        

        # Build scenes hierarchy
        appl.next_step = SceneStep(
            prepare = prep1,
            evaluate = eval1,

            next = SceneStep(
                prepare = prep2,
                evaluate = eval2,

                next = SceneStep(
                    prepare = prep3,
                    evaluate = eval3,

                    next = SceneStep(
                        prepare = prep4,
                        evaluate = eval4,

                        next = SceneStep(
                            prepare = prep5,
                            evaluate = eval5
                        )
                    )
                )
            )
        )

        with patch.dict(sys.modules, {
            "adafruit_display_shapes.roundrect": MockDisplayShapes().roundrect(),
            "adafruit_display_shapes.rect": MockDisplayShapes().rect()
        }):
            # Run process
            appl.process()


##################################################################################################


    # Tool to check if the passed pixels are white and the others not
    def _assert_enlightened(self, led_driver, pixels):
        for i in range(len(led_driver.leds)):
            led = led_driver.leds[i]

            if i in pixels:
                self.assertEqual(led, (255, 255, 255))
            else:
                self.assertNotEqual(led, (255, 255, 255))

    
