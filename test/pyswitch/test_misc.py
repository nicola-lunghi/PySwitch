import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

# Import subject under test
with patch.dict(sys.modules, {
    #"usb_midi": MockUsbMidi(),
    #"adafruit_midi": MockAdafruitMIDI(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "gc": MockGC()
}):
    from adafruit_midi.system_exclusive import SystemExclusive
    from adafruit_midi.control_change import ControlChange
    #from.mocks_appl import *
    from lib.pyswitch.misc import *



class TestMiscTools(unittest.TestCase):

    def test_stringify_midi_message_falsy(self):
        self.assertEqual(Tools.stringify_midi_message(None), repr(None))
        self.assertEqual(Tools.stringify_midi_message(0), repr(0))


##############################################################################


    def test_stringify_midi_message_sysex(self):
        message = SystemExclusive(
            manufacturer_id = [0x02, 0x03],
            data = [0x34, 0x45, 0x67]
        )

        str = Tools.stringify_midi_message(message)

        self.assertIn("SystemExclusive", str)
        self.assertIn("[2, 3]", str)
        self.assertIn("[34, 45, 67]", str)
        

##############################################################################


    def test_stringify_midi_message_cc(self):
        message = ControlChange(2, 66)

        str = Tools.stringify_midi_message(message)

        self.assertIn("ControlChange", str)
        self.assertIn("2", str)
        self.assertIn("66", str)
        

##############################################################################


    def test_stringify_midi_message_others(self):
        message = "nomessage"

        str = Tools.stringify_midi_message(message)

        self.assertIn("nomessage", str)
        

##############################################################################


    def test_compare_midi_messagess_sysex(self):
        message_1 = SystemExclusive(
            manufacturer_id = [0x02, 0x03],
            data = [0x34, 0x45, 0x67]
        )
        message_2 = SystemExclusive(
            manufacturer_id = [0x02, 0x03],
            data = [0x34, 0x45, 0x67]
        )

        self.assertEqual(Tools.compare_midi_messages(message_1, message_2), True)
        self.assertEqual(Tools.compare_midi_messages(message_1, None), False)
        self.assertEqual(Tools.compare_midi_messages(None, message_2), False)

        message_1.data[1] = 0xa9
        self.assertEqual(Tools.compare_midi_messages(message_1, message_2), False)

        message_1.data[1] = 0x45
        self.assertEqual(Tools.compare_midi_messages(message_1, message_2), True)

        message_1.manufacturer_id[1] = 0x04
        self.assertEqual(Tools.compare_midi_messages(message_1, message_2), False)


##############################################################################


    def test_compare_midi_messagess_cc(self):
        message_1 = ControlChange(2, 66)
        message_2 = ControlChange(2, 66)

        self.assertEqual(Tools.compare_midi_messages(message_1, message_2), True)
        self.assertEqual(Tools.compare_midi_messages(message_1, None), False)
        self.assertEqual(Tools.compare_midi_messages(None, message_2), False)

        message_1.control = 67

        self.assertEqual(Tools.compare_midi_messages(message_1, message_2), False)


##############################################################################


    def test_compare_midi_messagess_others(self):
        message_1 = "foo"
        message_2 = "bar"

        self.assertEqual(Tools.compare_midi_messages(message_1, message_2), False)



##############################################################################


class TestMiscUpdater(unittest.TestCase):

    def test_update(self):
        self.fail()