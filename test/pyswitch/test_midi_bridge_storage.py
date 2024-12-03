import sys
import unittest
from unittest.mock import patch, mock_open

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
    "gc": MockGC(),
    "os": MockOs
}):
    from .mocks_misc import MockMisc

    with patch.dict(sys.modules, {
        "lib.pyswitch.misc": MockMisc
    }):
        from lib.pyswitch.controller.MidiBridgeWrapper import _StorageProvider

        from.mocks_appl import *


class TestMidiBridgeWrapper(unittest.TestCase):

    def test_size(self):
        storage = _StorageProvider(
            temp_file_path = "temp"
        )

        MockOs.STAT_SIZE_OUTPUTS = {
            "foo": 5,
            "bar": 788
        }

        self.assertEqual(storage.size("foo"), 5)
        self.assertEqual(storage.size("bar"), 788)
        self.assertLess(storage.size("xxx"), 0)


    def test_read(self):
        storage = _StorageProvider(
            temp_file_path = "temp"
        )

        with patch("builtins.open", mock_open(read_data = "temporary")):
            handle = storage.open("foo", "r")

            self.assertEqual(handle.read(4), "temp")
            self.assertEqual(handle.read(4), "orar")
            self.assertEqual(handle.read(4), "y")
            self.assertTrue(not handle.read(4))


    def test_write(self):
        MockOs.RENAME_CALLS = []
        
        storage = _StorageProvider(
            temp_file_path = "temp"
        )

        writer = MockWriter()
        opener = mock_open()
        opener.return_value.write = writer.write

        with patch("builtins.open", opener) as mock_file_open:
            handle = storage.open("foo", "a")
            handle.write("some data")
            handle.close()

        # Check calls
        mock_file_open.assert_has_calls([
            # Clear
            unittest.mock.call("temp", "w"),
            unittest.mock.call().close(),
            # Write
            unittest.mock.call("temp", "a"),
            unittest.mock.call().close(),
        ])

        self.assertEqual(MockOs.RENAME_CALLS, [{ 
            "source": "temp",
            "target": "foo"
        }])        



        