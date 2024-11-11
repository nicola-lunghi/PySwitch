import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

# Import subject under test
with patch.dict(sys.modules, {
    "micropython": MockMicropython,
    "displayio": MockDisplayIO(),
    "adafruit_display_text": MockAdafruitDisplayText(),
    "usb_midi": MockUsbMidi(),
    "adafruit_midi": MockAdafruitMIDI(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "gc": MockGC()
}):
    from .mocks_misc import MockMisc

    with patch.dict(sys.modules, {
        "lib.pyswitch.misc": MockMisc()
    }):
        
        from .mocks_appl import *
        from .mocks_ui import *



class TestControllerDebug(unittest.TestCase):

    def test_debug(self):
        MockMisc.Tools.reset()

        switch_1 = MockSwitch()
        switch_2 = MockSwitch()
        
        action_1 = MockAction()
        action_2 = MockAction()
        action_3 = MockAction()

        period = MockPeriodCounter()

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
                },
                {
                    "assignment": {
                        "model": switch_2
                    },
                    "actions": [
                        action_2,
                        action_3
                    ]
                }
            ],
            period_counter = period,
            config = {
                "debug": True
            }
        )

        self.assertEqual(len(MockMisc.Tools.msgs), 2)

        # Build scene
        def eval1():            
            return False

        appl.next_step = SceneStep(
            evaluate = eval1
        )

        appl.process()

        self.assertEqual(len(MockMisc.Tools.msgs), 3)


##################################################################################


    def test_debug_with_ui(self):
        MockMisc.Tools.reset()

        switch_1 = MockSwitch()
        switch_2 = MockSwitch()
        
        action_1 = MockAction()
        action_2 = MockAction()
        action_3 = MockAction()

        period = MockPeriodCounter()

        ui = MockUiController()

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
                },
                {
                    "assignment": {
                        "model": switch_2
                    },
                    "actions": [
                        action_2,
                        action_3
                    ]
                }
            ],
            period_counter = period,
            config = {
                "debug": True
            },
            ui = ui
        )

        self.assertEqual(len(MockMisc.Tools.msgs), 2)

        # Build scene
        def eval1():            
            return False

        appl.next_step = SceneStep(
            evaluate = eval1
        )

        appl.process()

        self.assertEqual(len(MockMisc.Tools.msgs), 3)


##################################################################################


#    def test_debug_with_ui_structure(self):
#        switch_1 = MockSwitch()
#        period = MockPeriodCounter()
#
#        ui = MockUiController()
#
#        appl = MockController(
#            led_driver = MockNeoPixelDriver(),
#            communication = {
#                "valueProvider": MockValueProvider()
#            },
#            midi = MockMidiController(),
#            switches = [
#                {
#                    "assignment": {
#                        "model": switch_1
#                    }
#                }
#            ],
#            period_counter = period,
#            config = {
#                "debugUserInterfaceStructure": True
#            },
#            ui = ui
#        )
#
#        # Build scene
#        def eval1():            
#            return False
#
#        appl.next_step = SceneStep(
#            evaluate = eval1
#        )
#
#       appl.process()
#
#        self.assertEqual(ui.root.num_print_calls, 1)


##################################################################################


    def test_debug_reset_switches(self):
        MockMisc.Tools.reset()
        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            communication = {
                "valueProvider": MockValueProvider()
            },
            midi = MockMidiController(),
            config = {
                "debug": True
            }
        )

        self.assertEqual(len(MockMisc.Tools.msgs), 2)

        appl.reset_switches()

        self.assertEqual(len(MockMisc.Tools.msgs), 3)