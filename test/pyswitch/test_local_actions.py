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
    
    from lib.pyswitch.ui.elements import DisplayLabel
    from lib.pyswitch.controller.callbacks import BinaryParameterCallback
    from lib.pyswitch.misc import Updater
    
    from .mocks_appl import *
    from .mocks_callback import *

    from lib.pyswitch.clients.local.actions.binary_switch import *
    

class TestLocalActionDefinitions(unittest.TestCase):

    def test_binary_switch(self):
        mapping_1 = MockParameterMapping(
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0x09]
            )
        )

        display = DisplayLabel(layout = {
            "font": "foo"
        })

        ecb = MockEnabledCallback()

        action = BINARY_SWITCH(
            mapping = mapping_1,
            display = display, 
            text = "foo", 
            mode = PushButtonAction.LATCH, 
            color = (2, 3, 4), 
            id = 45, 
            use_leds = True, 
            enable_callback = ecb,
            value_on = 3,
            value_off = 5,
            reference_value = 6,
            comparison_mode = BinaryParameterCallback.LESS
        )

        cb = action.callback
        self.assertIsInstance(cb, BinaryParameterCallback)
        self.assertIsInstance(action, PushButtonAction)

        self.assertEqual(cb.mapping, mapping_1)
        self.assertEqual(cb._value_enable, 3)
        self.assertEqual(cb._value_disable, 5)
        self.assertEqual(cb._BinaryParameterCallback__reference_value, 6)
        self.assertEqual(cb._text, "foo")
        self.assertEqual(cb._color, (2, 3, 4))
        self.assertEqual(cb._BinaryParameterCallback__comparison_mode, BinaryParameterCallback.LESS)

        self.assertEqual(action.label, display)
        self.assertEqual(action.id, 45)
        self.assertEqual(action.uses_switch_leds, True)
        self.assertEqual(action._Action__enable_callback, ecb)


    