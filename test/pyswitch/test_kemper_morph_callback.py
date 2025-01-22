import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

# Import subject under test
with patch.dict(sys.modules, {
    "micropython": MockMicropython,
    "displayio": MockDisplayIO(),
    "adafruit_display_text": MockAdafruitDisplayText(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "adafruit_midi.program_change": MockAdafruitMIDIProgramChange(),
    "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
    "gc": MockGC()
}):
    from adafruit_midi.system_exclusive import SystemExclusive
    
    from lib.pyswitch.clients.kemper.actions.morph import KemperMorphCallback
    from lib.pyswitch.misc import Colors, compare_midi_messages
    from lib.pyswitch.controller.callbacks import BinaryParameterCallback
    from lib.pyswitch.controller.Controller import Controller
    
    from .mocks_appl import *
    from .mocks_callback import *


class TestKemperMorphCallback(unittest.TestCase):

    def test_colors(self):
        switch_1 = MockSwitch()
        
        mapping_1 = MockParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x01, 0x02, 0x03, 0x04]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0x09]
            )
        )

        cb = KemperMorphCallback(
            mapping = mapping_1, 
            text = "foo", 
            value_enable = 127, 
            value_disable = 0, 
            reference_value = 8191, 
            comparison_mode = BinaryParameterCallback.GREATER_EQUAL, 
            led_brightness_on = 0.5,
            led_brightness_off = 0.1,
            display_dim_factor_on = 0.5,
            display_dim_factor_off = 0.1
        )

        self.assertIsInstance(cb, BinaryParameterCallback)
        self.assertEqual(cb._BinaryParameterCallback__text, "foo")

        action_1 = PushButtonAction({
            "mode": PushButtonAction.MOMENTARY,
            "callback": cb,
            "useSwitchLeds": True          
        })
        
        led_driver = MockNeoPixelDriver()
        midi = MockMidiController()
        period = MockPeriodCounter()

        appl = Controller(
            led_driver = led_driver,
            midi = midi,
            inputs = [
                {
                    "assignment": {
                        "model": switch_1,
                        "pixels": [0]
                    },
                    "actions": [
                        action_1                        
                    ]
                },
                MockInputControllerDefinition()
            ],
            period_counter = period
        )

        appl.init()

        answer_msg = SystemExclusive(
            manufacturer_id = [0xbb, 0x10, 0x25],
            data = [0xaa, 0x00, 0x07, 0x47]
        )

        # Build scene:
        # Step 1
        midi.next_receive_messages = [
            answer_msg
        ]
        mapping_1.outputs_parse = [
            {
                "message": answer_msg,
                "value": 0
            }
        ]

        appl.tick()
        appl.tick()
        
        self.assertEqual(appl.inputs[0].color, Colors.RED)
        self.assertAlmostEqual(appl.inputs[0].brightness, 0.1)            
        
        # Step 2
        midi.next_receive_messages = [
            answer_msg
        ]
        mapping_1.outputs_parse = [
            {
                "message": answer_msg,
                "value": 16383
            }
        ]    

        appl.tick()
        appl.tick()
        
        self.assertEqual(appl.inputs[0].color, Colors.BLUE)
        self.assertEqual(appl.inputs[0].brightness, 0.5)
                    
        # Step 3
        midi.next_receive_messages = [
            answer_msg
        ]
        mapping_1.outputs_parse = [
            {
                "message": answer_msg,
                "value": 8191
            }
        ]    

        appl.tick()
        appl.tick()
        
        self.assertEqual(appl.inputs[0].color, (128, 0, 127))
        self.assertEqual(appl.inputs[0].brightness, 0.5)
                

#############################################################################################

    def test_suppress_send(self):
        self._test_suppress_send(False)
        self._test_suppress_send(True)


    def _test_suppress_send(self, suppress_send):
        switch_1 = MockSwitch()
        
        mapping_1 = MockParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x01, 0x02, 0x03, 0x04]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0x09]
            )
        )

        cb = KemperMorphCallback(
            mapping = mapping_1, 
            value_enable = 127, 
            value_disable = 0, 
            suppress_send = suppress_send
        )

        action_1 = PushButtonAction({
            "mode": PushButtonAction.MOMENTARY,
            "callback": cb,
            "useSwitchLeds": True          
        })
        
        led_driver = MockNeoPixelDriver()
        midi = MockMidiController()
        period = MockPeriodCounter()

        appl = Controller(
            led_driver = led_driver,
            midi = midi,
            inputs = [
                {
                    "assignment": {
                        "model": switch_1,
                        "pixels": [0]
                    },
                    "actions": [
                        action_1                        
                    ]
                },
                MockInputControllerDefinition()
            ],
            period_counter = period
        )

        appl.init()

        # Build scene:
        # Step 1
        switch_1.shall_be_pushed = True

        appl.tick()
        appl.tick()
        
        if suppress_send:
            self.assertEqual(len(mapping_1.set_value_calls), 0)    
            self.assertEqual(len(appl._Controller__midi.messages_sent), 0)
        else:
            self.assertEqual(len(mapping_1.set_value_calls), 1)
            self.assertEqual(mapping_1.set_value_calls[0], 127)

            self.assertEqual(len(appl._Controller__midi.messages_sent), 1)
            self.assertTrue(compare_midi_messages(appl._Controller__midi.messages_sent[0], mapping_1.set))
            
        # Step 2
        switch_1.shall_be_pushed = False
        
        appl.tick()
        appl.tick()
        
        if suppress_send:
            self.assertEqual(len(mapping_1.set_value_calls), 0)    
            self.assertEqual(len(appl._Controller__midi.messages_sent), 0)
        else:
            self.assertEqual(len(mapping_1.set_value_calls), 2)
            self.assertEqual(mapping_1.set_value_calls[1], 0)

            self.assertEqual(len(appl._Controller__midi.messages_sent), 2)
            self.assertTrue(compare_midi_messages(appl._Controller__midi.messages_sent[1], mapping_1.set))

