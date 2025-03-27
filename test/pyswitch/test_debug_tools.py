import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

# Import subject under test
with patch.dict(sys.modules, {
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "adafruit_midi.program_change": MockAdafruitMIDIProgramChange(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "gc": MockGC(),
    "time": MockTime
}):
    from adafruit_midi.system_exclusive import SystemExclusive
    from adafruit_midi.control_change import ControlChange
    from adafruit_midi.program_change import ProgramChange
    from adafruit_midi.midi_message import MIDIUnknownEvent
    
    from lib.pyswitch.debug_tools import *


##############################################################################


class TestDebugTools(unittest.TestCase):

    def test_stringify_midi_message_falsy(self):
        self.assertEqual(stringify_midi_message(None), repr(None))
        self.assertEqual(stringify_midi_message(0), repr(0))


    def test_stringify_midi_message_sysex(self):
        message = SystemExclusive(
            manufacturer_id = [0x02, 0x03],
            data = [0x34, 0x45, 0x67]
        )

        str = stringify_midi_message(message)

        self.assertIn("SystemExclusive", str)
        self.assertIn("[2, 3]", str)
        self.assertIn("[34, 45, 67]", str)
        

    def test_stringify_midi_message_cc(self):
        message = ControlChange(2, 66)

        str = stringify_midi_message(message)

        self.assertIn("ControlChange", str)
        self.assertIn("2", str)
        self.assertIn("66", str)


    def test_stringify_midi_message_pc(self):
        message = ProgramChange(56)

        str = stringify_midi_message(message)

        self.assertIn("ProgramChange", str)
        self.assertIn("56", str)


    def test_stringify_midi_message_ue(self):
        message = MIDIUnknownEvent(33)

        str = stringify_midi_message(message)

        self.assertIn("MIDIUnknownEvent", str)
        self.assertIn("33", str)


    def test_stringify_midi_message_others(self):
        message = "nomessage"

        str = stringify_midi_message(message)

        self.assertIn("nomessage", str)

