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
    "adafruit_midi.program_change": MockAdafruitMIDIProgramChange(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "adafruit_midi.start": MockAdafruitMIDIStart(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "gc": MockGC()
}):
    from .mocks_measurements import *

    with patch.dict(sys.modules, {
        "lib.pyswitch.controller.RuntimeMeasurement": MockMeasurements
    }):
        
        from .mocks_appl import *


class TestControllerMeasurementsCalls(unittest.TestCase):

    def test_runtime_measurement_tick_time(self):
        action_1 = MockAction()
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
                        "model": MockSwitch()
                    },
                    "actions": [
                        action_1                        
                    ]
                }
            ],
            period_counter = period
        )

        m = appl._measurement_tick_time

        # Build scene
        def prep1():            
            period.exceed_next_time = True
        
        def eval1():            
            self.assertEqual(m.num_update_calls, 1)
            self.assertEqual(m.num_start_calls, 6)
            self.assertEqual(m.num_finish_calls, 6)     

            self.assertEqual(appl.get_measurement(Controller.STAT_ID_TICK_TIME), m)
            self.assertEqual(appl.get_measurement(Controller.STAT_ID_TICK_TIME + 1), None)

            return False

        appl.next_step = SceneStep(
            num_pass_ticks = 5,
            prepare = prep1,
            evaluate = eval1
        )

        appl.process()

