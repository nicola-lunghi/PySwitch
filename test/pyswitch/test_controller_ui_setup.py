import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

# Import subject under test
with patch.dict(sys.modules, {
    "micropython": MockMicropython,
    "displayio": MockDisplayIO(),
    "adafruit_display_text": MockAdafruitDisplayText(),
    "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
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
       
        from lib.pyswitch.ui.ui import DisplayElement, HierarchicalDisplayElement
        from lib.pyswitch.ui.UiController import UiController

        from gc import gc_mock_data
        from .mocks_appl import *
        from .mocks_ui import MockDisplayDriver, MockFontLoader, MockUpdateableDisplayElement


class MockUiController(UiController):
    def __init__(self, display_driver = MockDisplayDriver(), font_loader = MockFontLoader(), root = None):        
        super().__init__(display_driver, font_loader, root)

        self.num_show_calls = 0

    def show(self):
        self.num_show_calls += 1


class TestControllerUiSetup(unittest.TestCase):

    def test_setup(self):
        switch_1 = MockSwitch()        
        action_1 = MockAction()
        period = MockPeriodCounter()

        element_1 = DisplayElement(id = 1)
        element_2 = DisplayElement(id = 2)
        element_3 = MockUpdateableDisplayElement(id = 3)

        ui = MockUiController(
            root = HierarchicalDisplayElement(
                children = [
                    element_1,
                    element_2,
                    element_3
                ]
            )
        )

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            communication = {
                "valueProvider": MockValueProvider()
            },
            midi = MockMidiController(),
            switches = [
                {
                    "assignment": {
                        "model": switch_1
                    },
                    "actions": [
                        action_1                        
                    ]
                }
            ],
            period_counter = period,
            ui = ui
        )

       # Build scene
        def prep1():      
            period.exceed_next_time = True      
            pass

        def eval1():            
            self.assertEqual(element_3.num_update_calls, 1)
            return False

        appl.next_step = SceneStep(
            prepare = prep1,
            evaluate = eval1
        )

        appl.process()

        self.assertEqual(ui.num_show_calls, 1)


    def test_low_mem_warning_above(self):
        gc_mock_data().reset()
        gc_mock_data().output_mem_free_override(20)

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            communication = {
                "valueProvider": MockValueProvider()
            },
            midi = MockMidiController(),
            config = {
                "memoryWarnLimitBytes": 1024
            }
        )
        
        def eval1():            
            return False

        appl.next_step = SceneStep(
            evaluate = eval1
        )

        appl.process()

        self.assertEqual(appl.low_memory_warning, True)


    def test_low_mem_warning_below(self):
        gc_mock_data().reset()
        gc_mock_data().output_mem_free_override(2048)

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            communication = {
                "valueProvider": MockValueProvider()
            },
            midi = MockMidiController(),
            config = {
                "memoryWarnLimitBytes": 1024
            }
        )
        
        def eval1():            
            return False

        appl.next_step = SceneStep(
            evaluate = eval1
        )

        appl.process()

        self.assertEqual(appl.low_memory_warning, False)

