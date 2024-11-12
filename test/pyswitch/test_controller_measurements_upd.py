import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

# Import subject under test
with patch.dict(sys.modules, {
    "micropython": MockMicropython,
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
        from .mocks_appl import *

        from lib.pyswitch.controller.RuntimeMeasurement import RuntimeMeasurement


class TestControllerMeasurementsUpdate(unittest.TestCase):

    def test_runtime_measurement_tick_time(self):
        action_1 = MockAction()
        period = MockPeriodCounter()

        MockGC.mock["collectCalls"] = 0
        MockMisc.reset_mock()

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            communication = {
                "valueProvider": MockValueProvider()
            },
            midi = MockMidiController(),
            switches = [
                {
                    "assignment": {
                        "model": MockSwitch()
                    },
                    "actions": [
                        action_1                        
                    ]
                }
            ],
            period_counter = period,
            config = {
                "debugStats": True
            }
        )

        m = appl._measurement_tick_time
        self.assertIsInstance(m, RuntimeMeasurement)

        MockGC.mock["memFreeReturn"] = 56

        # Build scene
        def prep1():            
            period.exceed_next_time = True
        
        def eval1():            
            self.assertEqual(MockGC.mock["collectCalls"], 1)
            self.assertIn(MockMisc.format_size(MockGC.mock["memFreeReturn"]), MockMisc.msgs_str)
            return False

        appl.next_step = SceneStep(
            num_pass_ticks = 5,
            prepare = prep1,
            evaluate = eval1
        )

        appl.process()

