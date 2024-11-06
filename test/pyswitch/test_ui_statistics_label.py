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
    from .mocks_measurements import *

    with patch.dict(sys.modules, {
        "lib.pyswitch.controller.measurements": MockMeasurements()
    }):

        from lib.pyswitch.ui.ui import DisplayBounds
        from lib.pyswitch.ui.elements import StatisticsDisplayLabel

        from .mocks_ui import *


class MockController:
    def __init__(self):
        self.added = []

    def add_runtime_measurement(self, m):
        self.added.append(m)


class TestStatisticsDisplayLabel(unittest.TestCase):

    def test_runtime(self):
        m1 = MockMeasurements.RuntimeMeasurement()
        m2 = MockMeasurements.RuntimeMeasurement()

        display = StatisticsDisplayLabel(
            measurements = [m1, m2],
            bounds = DisplayBounds(20, 30, 200, 300),
            layout = {
                "font": "foo"
            }      
        )

        ui = MockDisplaySplash()
        appl = MockController()

        display.init(ui, appl)

        self.assertEqual(appl.added, [m1, m2])
        
        m1.output_message = "foo"
        m2.output_message = "bar"

        display.measurement_updated(m1)
        display.measurement_updated(m2)
        display.update()

        self.assertEqual(display.text, "foo\nbar")

        display.measurement_updated(m1)
        display.measurement_updated(m2)
        display.update()

        self.assertEqual(display.text, "foo\nbar")


    def test_freemem(self):
        m1 = MockMeasurements.FreeMemoryMeasurement()
        m2 = MockMeasurements.FreeMemoryMeasurement()

        display = StatisticsDisplayLabel(
            measurements = [m1, m2],
            bounds = DisplayBounds(20, 30, 200, 300),
            layout = {
                "font": "foo"
            }      
        )

        ui = MockDisplaySplash()
        appl = MockController()

        display.init(ui, appl)

        self.assertEqual(appl.added, [m1, m2])
        
        m1.output_message = "foo"
        m2.output_message = "bar"

        display.measurement_updated(m1)
        display.measurement_updated(m2)
        display.update()

        self.assertEqual(display.text, "foo\nbar")

        display.measurement_updated(m1)
        display.measurement_updated(m2)
        display.update()

        self.assertEqual(display.text, "foo\nbar")
