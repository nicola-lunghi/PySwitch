import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

# Import subject under test
with patch.dict(sys.modules, {
    "usb_midi": MockUsbMidi(),
    "adafruit_midi": MockAdafruitMIDI(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "gc": MockGC(),
    "time": MockTime
}):
    from lib.pyswitch.controller.measurements import RuntimeMeasurement, FreeMemoryMeasurement
    from lib.pyswitch.misc import Tools


class MockRuntimeMeasurementListener:
    def __init__(self):
        self.num_update_calls = 0

    def measurement_updated(self, measurement):
        self.num_update_calls += 1


class TestMeasurementRuntime(unittest.TestCase):    

    def test_measurement(self):
        m = RuntimeMeasurement(
            interval_millis = 300,
            type = "foo"
        )

        self.assertEqual(m.type, "foo")
        self.assertEqual(m.average, 0)
        self.assertEqual(m.value(), 0)

        # finish without start: Must be ignored
        MockTime.mock["monotonicReturn"] = 0.9
        m.finish()

        msg = m.get_message()
        self.assertIn("No data", msg)

        # Tick with 500ms
        MockTime.mock["monotonicReturn"] = 1
        m.start()
        MockTime.mock["monotonicReturn"] = 1.5
        m.finish()

        self.assertEqual(m.average, 500)
        self.assertEqual(m.value(), 500)

        msg = m.get_message()
        self.assertIn("foo", msg)
        self.assertIn("500ms", msg)

        # Tick with 300ms
        MockTime.mock["monotonicReturn"] = 2
        m.start()
        MockTime.mock["monotonicReturn"] = 2.3
        m.finish()

        self.assertEqual(m.average, 400)
        self.assertEqual(m.value(), 500)

        msg = m.get_message()
        self.assertIn("foo", msg)
        self.assertIn("500ms", msg)
        self.assertIn("400ms", msg)

        # Tick with 1000ms
        MockTime.mock["monotonicReturn"] = 3
        m.start()
        MockTime.mock["monotonicReturn"] = 4
        m.finish()

        self.assertEqual(m.average, 600)
        self.assertEqual(m.value(), 1000)

        msg = m.get_message()
        self.assertIn("foo", msg)
        self.assertIn("600ms", msg)
        self.assertIn("1000ms", msg)

        m.reset()
        self.assertEqual(m.average, 0)
        self.assertEqual(m.value(), 0)


    def test_update(self):
        m = RuntimeMeasurement(
            interval_millis = 300,
            type = "foo"
        )

        listener_1 = MockRuntimeMeasurementListener()
        listener_2 = MockRuntimeMeasurementListener()
        m.add_listener(listener_1)
        m.add_listener(listener_2)

        MockTime.mock["monotonicReturn"] = 1

        m.update()
        self.assertEqual(listener_1.num_update_calls, 1)
        self.assertEqual(listener_2.num_update_calls, 1)

        MockTime.mock["monotonicReturn"] = 1.2

        m.update()
        self.assertEqual(listener_1.num_update_calls, 1)
        self.assertEqual(listener_2.num_update_calls, 1)

        MockTime.mock["monotonicReturn"] = 1.4

        m.update()
        self.assertEqual(listener_1.num_update_calls, 2)
        self.assertEqual(listener_2.num_update_calls, 2)

        MockTime.mock["monotonicReturn"] = 1.6

        m.update()
        self.assertEqual(listener_1.num_update_calls, 2)
        self.assertEqual(listener_2.num_update_calls, 2)

        MockTime.mock["monotonicReturn"] = 1.8

        m.update()
        self.assertEqual(listener_1.num_update_calls, 3)
        self.assertEqual(listener_2.num_update_calls, 3)


#################################################################################


class TestMeasurementFreeMemory(unittest.TestCase):    

    def test_measurement(self):
        MockGC.mock = {
            "collectCalls": 0,
            "memFreeReturn": 1000
        }

        m = FreeMemoryMeasurement()
        
        self.assertEqual(m.value(), 1000)
        self.assertEqual(MockGC.mock["collectCalls"], 1)
        self.assertIn(Tools.format_size(1000), m.get_message())
        self.assertEqual(MockGC.mock["collectCalls"], 2)

        MockGC.mock["memFreeReturn"] = 222
        self.assertEqual(m.value(), 222)
        self.assertEqual(MockGC.mock["collectCalls"], 3)
        self.assertIn(Tools.format_size(222), m.get_message())


        
