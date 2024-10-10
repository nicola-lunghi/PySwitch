import sys
import unittest
from unittest.mock import patch

#################################################################################################

class MockUsbMidi:
    ports = [None, None]

class MockAdafruitMIDI:
    class MIDI:
        def __init__(self, midi_out, out_channel, midi_in, in_buf_size, debug):
            pass

        def receive(self):
            return None
        
        def send(self, midi_message):
            pass
            
class MockAdafruitMIDIControlChange:    
    class ControlChange:
        def __init__(self, control, value):
            self.control = control
            self.value = value

class MockAdafruitMIDISystemExclusive:    
    class SystemExclusive:
        def __init__(self, manufacturer_id = [0x00, 0x00, 0x00], data = []):
            self.manufacturer_id = manufacturer_id
            self.data = data

class MockGC:
    def collect():
        pass

    def mem_free():
        return 0

    def mem_alloc():
        return 0

#################################################################################################

with patch.dict(sys.modules, {
    "usb_midi": MockUsbMidi(),
    "adafruit_midi": MockAdafruitMIDI(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "gc": MockGC()
}):
    from lib.pyswitch.controller.Controller import Controller

#################################################################################################

class TestSimpleConfig(unittest.TestCase):
    def test_simple(self):
        appl = Controller(
            led_driver = None,
            config = {

            },
            value_provider = None,
            switches = [],
            displays = [],
            ui = None            
        )
        
