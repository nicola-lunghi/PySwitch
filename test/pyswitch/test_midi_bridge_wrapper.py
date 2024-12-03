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
    "pymidibridge": MockMidiBridge,
    "gc": MockGC()
}):
    from adafruit_midi.system_exclusive import SystemExclusive

    from lib.pyswitch.controller.MidiBridgeWrapper import MidiBridgeWrapper

    from.mocks_appl import *



class TestMidiBridgeWrapper(unittest.TestCase):

    def test_send(self):
        midi = MockMidiController()

        bridge = MidiBridgeWrapper(
            midi = midi,
            temp_file_path = "temp"
        )

        midi_message = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x01, 0x02, 0x03, 0x04]
        ),

        bridge.send(midi_message)

        self.assertEqual(midi.messages_sent, [midi_message])


    def test_receive(self):
        midi = MockMidiController()

        bridge = MidiBridgeWrapper(
            midi = midi,
            temp_file_path = "temp"
        )

        result = bridge.receive()
        self.assertEqual(bridge._bridge.messages_received, [])

        midi_message = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x01, 0x02, 0x03, 0x04]
        ),

        midi.next_receive_messages = [midi_message]

        result = bridge.receive()

        self.assertEqual(result, midi_message)
        self.assertEqual(len(midi.next_receive_messages), 0)

        self.assertEqual(bridge._bridge.messages_received, [midi_message])


    def test_callbacks(self):
        midi = MockMidiController()

        bridge = MidiBridgeWrapper(
            midi = midi,
            temp_file_path = "temp"
        )

        bridge.send_system_exclusive(
            manufacturer_id = b'\x00\x20\x44',
            data = b'\x02'
        )

        last_msg = midi.messages_sent[0]
        
        self.assertIsInstance(last_msg, SystemExclusive)
        self.assertEqual(last_msg.manufacturer_id, b'\x00\x20\x44')
        self.assertEqual(last_msg.data, b'\x02')

