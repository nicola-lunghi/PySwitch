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
    
    from lib.pyswitch.clients.kemper import KemperActionDefinitions, KemperEffectEnableCallback, KemperEffectSlot, KemperMappings
    from lib.pyswitch.ui.elements import DisplayLabel
    from lib.pyswitch.controller.callbacks import BinaryParameterCallback
    
    from .mocks_appl import *
    from .mocks_callback import *


class TestKemperActionDefinitions(unittest.TestCase):

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

        action = KemperActionDefinitions.BINARY_SWITCH(
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

        self.assertEqual(cb._mapping, mapping_1)
        self.assertEqual(cb._value_enable, 3)
        self.assertEqual(cb._value_disable, 5)
        self.assertEqual(cb._reference_value, 6)
        self.assertEqual(cb._text, "foo")
        self.assertEqual(cb.color, (2, 3, 4))
        self.assertEqual(cb._comparison_mode, BinaryParameterCallback.LESS)

        self.assertEqual(action.label, display)
        self.assertEqual(action.id, 45)
        self.assertEqual(action.uses_switch_leds, True)
        self.assertEqual(action._enable_callback, ecb)


    def test_effect_state(self):
        display = DisplayLabel(layout = {
            "font": "foo"
        })

        ecb = MockEnabledCallback()

        action = KemperActionDefinitions.EFFECT_STATE(
            KemperEffectSlot.EFFECT_SLOT_ID_C, 
            display = display,
            mode = PushButtonAction.LATCH, 
            id = 45, 
            use_leds = True, 
            enable_callback = ecb
        )

        cb = action.callback
        self.assertIsInstance(cb, KemperEffectEnableCallback)
        self.assertIsInstance(action, PushButtonAction)

        self.assertEqual(cb.mapping_fxtype, KemperMappings.EFFECT_TYPE(KemperEffectSlot.EFFECT_SLOT_ID_C))
        
        self.assertEqual(action.label, display)
        self.assertEqual(action.id, 45)
        self.assertEqual(action.uses_switch_leds, True)
        self.assertEqual(action._enable_callback, ecb)
        self.assertEqual(action._mode, PushButtonAction.LATCH)


    def test_tuner_mode(self):
        display = DisplayLabel(layout = {
            "font": "foo"
        })

        ecb = MockEnabledCallback()

        action = KemperActionDefinitions.TUNER_MODE(
            display = display, 
            mode = PushButtonAction.ONE_SHOT, 
            color = (4, 5, 6), 
            id = 67, 
            use_leds = True, 
            enable_callback = ecb
        )

        cb = action.callback
        self.assertIsInstance(cb, BinaryParameterCallback)
        self.assertIsInstance(action, PushButtonAction)

        self.assertEqual(cb._mapping, KemperMappings.TUNER_MODE_STATE())
        self.assertEqual(cb._text, "Tuner")
        self.assertEqual(cb.color, (4, 5, 6))

        self.assertEqual(action.label, display)
        self.assertEqual(action.id, 67)
        self.assertEqual(action.uses_switch_leds, True)
        self.assertEqual(action._enable_callback, ecb)


    def test_tap_tempo(self):
        display = DisplayLabel(layout = {
            "font": "foo"
        })

        ecb = MockEnabledCallback()

        action = KemperActionDefinitions.TAP_TEMPO(
            display = display, 
            color = (4, 5, 6), 
            id = 67, 
            use_leds = True, 
            enable_callback = ecb
        )

        cb = action.callback
        self.assertIsInstance(cb, BinaryParameterCallback)
        self.assertIsInstance(action, PushButtonAction)

        self.assertEqual(cb._mapping, KemperMappings.TAP_TEMPO())
        self.assertEqual(cb._text, "Tap")
        self.assertEqual(cb.color, (4, 5, 6))

        self.assertEqual(action.label, display)
        self.assertEqual(action.id, 67)
        self.assertEqual(action.uses_switch_leds, True)
        self.assertEqual(action._enable_callback, ecb)


    def test_show_tempo(self):
        display = DisplayLabel(layout = {
            "font": "foo"
        })

        ecb = MockEnabledCallback()

        action = KemperActionDefinitions.SHOW_TEMPO(
            display = display, 
            color = (4, 5, 6), 
            text = "foo",
            id = 67, 
            use_leds = True, 
            enable_callback = ecb
        )

        cb = action.callback
        self.assertIsInstance(cb, BinaryParameterCallback)
        self.assertIsInstance(action, PushButtonAction)

        self.assertEqual(cb._mapping, KemperMappings.TEMPO_DISPLAY())
        self.assertEqual(cb._text, "foo")
        self.assertEqual(cb.color, (4, 5, 6))

        self.assertEqual(action.label, display)
        self.assertEqual(action.id, 67)
        self.assertEqual(action.uses_switch_leds, True)
        self.assertEqual(action._enable_callback, ecb)


    def test_effect_button(self):
        self._test_effect_button(1, None, "FX I")
        self._test_effect_button(2, None, "FX II")
        self._test_effect_button(3, None, "FX III")
        self._test_effect_button(4, None, "FX IIII")
        self._test_effect_button(5, None, None)

        self._test_effect_button(1, "foo", "foo")
        self._test_effect_button(4, "foo", "foo")

    def _test_effect_button(self, num, text, exp_text):
        display = DisplayLabel(layout = {
            "font": "foo"
        })

        ecb = MockEnabledCallback()

        action = KemperActionDefinitions.EFFECT_BUTTON(
            num = num,
            display = display, 
            color = (4, 5, 6), 
            text = text,
            id = 67, 
            use_leds = True, 
            enable_callback = ecb
        )

        cb = action.callback
        self.assertIsInstance(cb, BinaryParameterCallback)
        self.assertIsInstance(action, PushButtonAction)

        self.assertEqual(cb._mapping, KemperMappings.EFFECT_BUTTON(num))
        self.assertEqual(cb._text, exp_text)
        self.assertEqual(cb.color, (4, 5, 6))

        self.assertEqual(action.label, display)
        self.assertEqual(action.id, 67)
        self.assertEqual(action.uses_switch_leds, True)
        self.assertEqual(action._enable_callback, ecb)


    def test_morph_button(self):
        display = DisplayLabel(layout = {
            "font": "foo"
        })

        ecb = MockEnabledCallback()

        action = KemperActionDefinitions.MORPH_BUTTON(
            display = display, 
            color = (4, 5, 6), 
            text = "foo",
            id = 67, 
            use_leds = True, 
            enable_callback = ecb
        )

        cb = action.callback
        self.assertIsInstance(cb, BinaryParameterCallback)
        self.assertIsInstance(action, PushButtonAction)

        self.assertEqual(cb._mapping, KemperMappings.MORPH_BUTTON())
        self.assertEqual(cb._text, "foo")
        self.assertEqual(cb._value_enable, 1)
        self.assertEqual(cb._value_disable, 0)
        self.assertEqual(cb.color, (4, 5, 6))

        self.assertEqual(action.label, display)
        self.assertEqual(action.id, 67)
        self.assertEqual(action.uses_switch_leds, True)
        self.assertEqual(action._enable_callback, ecb)
        self.assertEqual(action._mode, PushButtonAction.MOMENTARY)


    def test_rig_volume_boost(self):
        self._test_rig_volume_boost(False, 0.75, int(16383 * 0.75), int(16383 * 0.5))
        self._test_rig_volume_boost(True, 0.85, int(16383 * 0.85), "auto")

    def _test_rig_volume_boost(self, remember_off_value, boost_volume, exp_value_enable, exp_value_disable):
        display = DisplayLabel(layout = {
            "font": "foo"
        })

        ecb = MockEnabledCallback()

        action = KemperActionDefinitions.RIG_VOLUME_BOOST(
            boost_volume = boost_volume, 
            mode = PushButtonAction.LATCH, 
            remember_off_value = remember_off_value, 
            display = display, 
            color = (4, 5, 6), 
            text = "foo",
            id = 67, 
            use_leds = True, 
            enable_callback = ecb
        )

        cb = action.callback
        self.assertIsInstance(cb, BinaryParameterCallback)
        self.assertIsInstance(action, PushButtonAction)

        self.assertEqual(cb._mapping, KemperMappings.RIG_VOLUME())
        self.assertEqual(cb._text, "foo")
        self.assertEqual(cb._value_enable, exp_value_enable)
        self.assertEqual(cb._value_disable, exp_value_disable)
        self.assertEqual(cb.color, (4, 5, 6))

        self.assertEqual(action.label, display)
        self.assertEqual(action.id, 67)
        self.assertEqual(action.uses_switch_leds, True)
        self.assertEqual(action._enable_callback, ecb)
        self.assertEqual(action._mode, PushButtonAction.LATCH)


    