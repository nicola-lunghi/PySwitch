import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

# Import subject under test
with patch.dict(sys.modules, {
    "displayio": MockDisplayIO(),
    "adafruit_display_text": MockAdafruitDisplayText(),
    "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
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

    #with patch.dict(sys.modules, {
    #    "lib.pyswitch.controller.RuntimeMeasurement": MockRuntimeMeasurement()
    #}):

    from lib.pyswitch.ui.ui import DisplayBounds
    from lib.pyswitch.ui.elements import PerformanceIndicator

    from .mocks_ui import *


class MockController:
    def __init__(self):
        self.output_get_measurement = None
        self.get_measurement_calls = []

    def get_measurement(self, id):
        self.get_measurement_calls.append(id)
        return self.output_get_measurement
        

class TestPerformanceIndicator(unittest.TestCase):

    def test(self):
        m = MockRuntimeMeasurement(
            interval_millis = 500
        )

        display = PerformanceIndicator(
            measurement_id = 33,
            bounds = DisplayBounds(20, 30, 200, 300)            
        )

        ui = MockDisplaySplash()
        appl = MockController()
        appl.output_get_measurement = m

        display.init(ui, appl)

        self.assertEqual(appl.get_measurement_calls, [33])
        
        dot = ui.splash[0]
        self.assertEqual(dot.fill, (0, 0, 0))

        m.output_value = 201

        display.measurement_updated(m)

        self.assertEqual(dot.fill, (0, 0, 0))

        # Ensure that all colors are getting brighter with value
        last_brightness = 0
        for i in range(202, 3000):
            m.output_value = i
            display.measurement_updated(m)

            brightness = dot.fill[0] + dot.fill[1] + dot.fill[2]

            self.assertGreaterEqual(brightness, last_brightness - 1, repr(i))  # We allow a deviance of 1

            last_brightness = brightness
            
