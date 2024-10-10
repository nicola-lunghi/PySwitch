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

#################################################################################################

with patch.dict(sys.modules, {
    "usb_midi": MockUsbMidi(),
    "adafruit_midi": MockAdafruitMIDI()
}):
    from lib.pyswitch.controller.Controller import Controller

#################################################################################################

class TestSimpleConfig(unittest.TestCase):
    def test_simple(self):
        appl = Controller(
            ui = None, 
            led_driver = None,
            config = {

            }
        )
        
