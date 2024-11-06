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
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "gc": MockGC()
}):
        
    from lib.pyswitch.ui.ui import DisplayElement, HierarchicalDisplayElement
    from lib.pyswitch.ui.UiController import UiController

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

        #self.assertEqual(len(ui.current.root.children), 3)

        #self.assertEqual(ui.current.root.child(0), element_1)
        #self.assertEqual(ui.current.root.child(1), element_2)
        #self.assertEqual(ui.current.root.child(2), element_3)

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

