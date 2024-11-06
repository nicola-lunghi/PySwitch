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
    "gc": MockGC()
}):
    from adafruit_midi.system_exclusive import SystemExclusive
    from adafruit_midi.midi_message import MIDIUnknownEvent
    from lib.pyswitch.controller.MidiController import MidiController, MidiRouting

    from.mocks_appl import *



class TestMidiController(unittest.TestCase):

    def test_appl_routing(self):
        sub_midi_1 = MockMidiController()
        sub_midi_2 = MockMidiController()

        # Must not throw
        midi = MidiController(
            config = {
                "routings": [
                    MidiRouting(
                        source = MidiController.APPLICATION,
                        target = sub_midi_2
                    ),                    
                    MidiRouting(
                        source = sub_midi_1,
                        target = MidiController.APPLICATION
                    )
                ]
            }
        )

        # Receive
        midi_message_1 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0x07, 0x45]
        )

        midi_message_2 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x22],
            data = [0x00, 0x00, 0x07, 0x47]
        )

        sub_midi_1.next_receive_messages = [
            midi_message_1,
            midi_message_2
        ]
        
        self.assertEqual(midi.receive(), midi_message_1)
        self.assertEqual(midi.receive(), midi_message_2)
        self.assertEqual(midi.receive(), None)

        self.assertEqual(sub_midi_1.messages_sent, [])
        self.assertEqual(sub_midi_2.messages_sent, [])

        # Send
        midi_message_3 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x22],
            data = [0x00, 0x00, 0xa8, 0x47]
        )

        midi.send(midi_message_3)
        self.assertEqual(sub_midi_2.messages_sent, [midi_message_3])


    def test_appl_routing_distribute(self):
        sub_midi_1 = MockMidiController()
        sub_midi_2 = MockMidiController()

        # Must not throw
        midi = MidiController(
            config = {
                "routings": [
                    MidiRouting(
                        source = MidiController.APPLICATION,
                        target = sub_midi_1
                    ),                    
                    MidiRouting(
                        source = MidiController.APPLICATION,
                        target = sub_midi_2
                    )
                ]
            }
        )

        # Receive
        midi_message_1 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0x07, 0x45]
        )

        midi_message_2 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x22],
            data = [0x00, 0x00, 0x07, 0x47]
        )

        midi.send(midi_message_1)
        self.assertEqual(sub_midi_1.messages_sent, [midi_message_1])
        self.assertEqual(sub_midi_2.messages_sent, [midi_message_1])

        midi.send(midi_message_2)
        self.assertEqual(sub_midi_1.messages_sent, [midi_message_1, midi_message_2])
        self.assertEqual(sub_midi_2.messages_sent, [midi_message_1, midi_message_2])


    def test_appl_routing_merge(self):
        sub_midi_1 = MockMidiController()
        sub_midi_2 = MockMidiController()

        # Must not throw
        midi = MidiController(
            config = {
                "routings": [
                    MidiRouting(
                        source = sub_midi_1,
                        target = MidiController.APPLICATION
                    ),                    
                    MidiRouting(
                        source = sub_midi_2,
                        target = MidiController.APPLICATION
                    )
                ]
            }
        )

        # Receive
        midi_message_1 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0x07, 0x45]
        )

        midi_message_2 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x22],
            data = [0x00, 0x00, 0x07, 0x47]
        )

        midi_message_3 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x22],
            data = [0x00, 0x00, 0x07, 0x88]
        )

        sub_midi_1.next_receive_messages = [
            midi_message_1,
            midi_message_2
        ]

        sub_midi_2.next_receive_messages = [
            midi_message_3
        ]
        
        self.assertEqual(midi.receive(), midi_message_1)
        self.assertEqual(midi.receive(), midi_message_2)
        self.assertEqual(midi.receive(), midi_message_3)        
        self.assertEqual(midi.receive(), None)

        self.assertEqual(sub_midi_1.messages_sent, [])
        self.assertEqual(sub_midi_2.messages_sent, [])        


###################################################################################################


    def test_external_routings_distribute(self):
        sub_midi_1 = MockMidiController()

        sub_midi_2 = MockMidiController()
        sub_midi_3 = MockMidiController()

        # Must not throw
        midi = MidiController(
            config = {
                "routings": [
                    MidiRouting(
                        source = sub_midi_1,
                        target = sub_midi_2
                    ),
                    MidiRouting(
                        source = sub_midi_1,
                        target = sub_midi_3
                    )
                ]
            }
        )

        midi_message_1 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0x07, 0x45]
        )

        midi_message_2 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x22],
            data = [0x00, 0x00, 0x07, 0x47]
        )

        midi_message_unknown = MIDIUnknownEvent(
            status = 248
        )

        sub_midi_1.next_receive_messages = [
            midi_message_1,            
            midi_message_2,
            midi_message_unknown
        ]

        # Receiving triggers external routes
        midi.receive()
        self.assertEqual(sub_midi_2.messages_sent, [midi_message_1])
        self.assertEqual(sub_midi_3.messages_sent, [midi_message_1])

        midi.receive()
        self.assertEqual(sub_midi_2.messages_sent, [midi_message_1, midi_message_2])
        self.assertEqual(sub_midi_3.messages_sent, [midi_message_1, midi_message_2])

        midi.receive()
        self.assertEqual(sub_midi_2.messages_sent, [midi_message_1, midi_message_2])
        self.assertEqual(sub_midi_3.messages_sent, [midi_message_1, midi_message_2])

        self.assertEqual(sub_midi_1.messages_sent, [])


    def test_external_routings_merge(self):
        sub_midi_1 = MockMidiController()
        sub_midi_2 = MockMidiController()

        sub_midi_3 = MockMidiController()

        # Must not throw
        midi = MidiController(
            config = {
                "routings": [
                    MidiRouting(
                        source = sub_midi_1,
                        target = sub_midi_3
                    ),
                    MidiRouting(
                        source = sub_midi_2,
                        target = sub_midi_3
                    )
                ]
            }
        )

        midi_message_1 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0x07, 0x45]
        )

        midi_message_2 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x22],
            data = [0x00, 0x00, 0x07, 0x47]
        )

        midi_message_3 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0x07, 0x45]
        )

        midi_message_4 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x22],
            data = [0x00, 0x00, 0x07, 0x47]
        )

        sub_midi_1.next_receive_messages = [
            midi_message_1,
            midi_message_2
        ]

        sub_midi_2.next_receive_messages = [
            midi_message_3,
            midi_message_4
        ]

        # Receiving triggers external routes
        midi.receive()
        self.assertEqual(sub_midi_3.messages_sent, [midi_message_1, midi_message_3])
        
        midi.receive()
        self.assertEqual(sub_midi_3.messages_sent, [midi_message_1, midi_message_3, midi_message_2, midi_message_4])
        
        midi.receive()
        self.assertEqual(sub_midi_3.messages_sent, [midi_message_1, midi_message_3, midi_message_2, midi_message_4])
        
        self.assertEqual(sub_midi_1.messages_sent, [])
        self.assertEqual(sub_midi_2.messages_sent, [])
        
        
    def test_no_args(self):
        # Must not throw
        MidiController()

