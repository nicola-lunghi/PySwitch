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
        
    from .mocks_appl import *
    from .mocks_ui import *


class TestControllerUiSetup(unittest.TestCase):

    def test_debug(self):
        switch_1 = MockSwitch()
        
        action_1 = MockAction()

        period = MockPeriodCounter()

        ui = MockUserInterface()

        element_1 = MockDisplayElement(id = 1)
        element_2 = MockDisplayElement(id = 2)
        element_3 = MockUpdateableDisplayElement(id = 3)

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            value_provider = MockValueProvider(),
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
            displays = [
                element_1,
                element_2,
                element_3
            ],
            ui = ui
        )

        self.assertEqual(len(ui.root.children), 3)

        self.assertEqual(ui.root.child(0), element_1)
        self.assertEqual(ui.root.child(1), element_2)
        self.assertEqual(ui.root.child(2), element_3)

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


##################################################################################
