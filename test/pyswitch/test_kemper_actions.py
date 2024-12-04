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
    
    from lib.pyswitch.clients.kemper import KemperActionDefinitions, KemperEffectEnableCallback, KemperEffectSlot, KemperMappings, KemperMorphCallback
    from lib.pyswitch.ui.elements import DisplayLabel
    from lib.pyswitch.controller.callbacks import BinaryParameterCallback, DEFAULT_LED_BRIGHTNESS_ON, DEFAULT_SLOT_DIM_FACTOR_ON
    
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
        self.assertEqual(cb._color, (2, 3, 4))
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
        self.assertEqual(cb._color, (4, 5, 6))

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
        self.assertEqual(cb._color, (4, 5, 6))

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
        self.assertEqual(cb._color, (4, 5, 6))

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
        self.assertEqual(cb._color, (4, 5, 6))

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
            text = "foo",
            id = 67, 
            color = (3, 4, 5),
            use_leds = True, 
            enable_callback = ecb
        )

        cb = action.callback
        self.assertIsInstance(cb, BinaryParameterCallback)
        self.assertIsInstance(action, PushButtonAction)

        self.assertEqual(cb._mapping, KemperMappings.MORPH_BUTTON())
        self.assertEqual(cb._text, "foo")
        self.assertEqual(cb._color, (3, 4, 5))
        self.assertEqual(cb._value_enable, 1)
        self.assertEqual(cb._value_disable, 0)

        self.assertEqual(action.label, display)
        self.assertEqual(action.id, 67)
        self.assertEqual(action.uses_switch_leds, True)
        self.assertEqual(action._enable_callback, ecb)
        self.assertEqual(action._mode, PushButtonAction.MOMENTARY)


    def test_morph_button_with_display(self):
        display = DisplayLabel(layout = {
            "font": "foo"
        })

        ecb = MockEnabledCallback()

        action = KemperActionDefinitions.MORPH_BUTTON_WITH_DISPLAY(
            display = display, 
            text = "foo",
            id = 67, 
            use_leds = True, 
            enable_callback = ecb
        )

        cb = action.callback
        self.assertIsInstance(cb, KemperMorphCallback)
        self.assertIsInstance(action, PushButtonAction)

        self.assertEqual(cb._mapping, KemperMappings.MORPH_BUTTON())
        self.assertEqual(cb._text, "foo")
        self.assertEqual(cb._value_enable, 1)
        self.assertEqual(cb._value_disable, 0)

        self.assertEqual(action.label, display)
        self.assertEqual(action.id, 67)
        self.assertEqual(action.uses_switch_leds, True)
        self.assertEqual(action._enable_callback, ecb)
        self.assertEqual(action._mode, PushButtonAction.MOMENTARY)


    def test_morph_display(self):
        display = DisplayLabel(layout = {
            "font": "foo"
        })

        ecb = MockEnabledCallback()

        action = KemperActionDefinitions.MORPH_DISPLAY(
            display = display, 
            text = "foo",
            id = 67, 
            use_leds = True, 
            enable_callback = ecb
        )

        cb = action.callback
        self.assertIsInstance(cb, KemperMorphCallback)
        self.assertIsInstance(action, PushButtonAction)

        self.assertEqual(cb._mapping, KemperMappings.MORPH_PEDAL())
        self.assertEqual(cb._text, "foo")
        self.assertEqual(cb._comparison_mode, BinaryParameterCallback.NO_STATE_CHANGE)
        self.assertEqual(cb._led_brightness_off, DEFAULT_LED_BRIGHTNESS_ON)

        self.assertEqual(cb._display_dim_factor_off, DEFAULT_SLOT_DIM_FACTOR_ON)
        self.assertEqual(cb._suppress_send, True)
        
        self.assertEqual(action.label, display)
        self.assertEqual(action.id, 67)
        self.assertEqual(action.uses_switch_leds, True)
        self.assertEqual(action._enable_callback, ecb)


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
        self.assertEqual(cb._color, (4, 5, 6))

        self.assertEqual(action.label, display)
        self.assertEqual(action.id, 67)
        self.assertEqual(action.uses_switch_leds, True)
        self.assertEqual(action._enable_callback, ecb)
        self.assertEqual(action._mode, PushButtonAction.LATCH)


    def test_rig_select_and_morph(self):
        display_select = DisplayLabel(layout = {
            "font": "foo"
        })
        display_morph = DisplayLabel(layout = {
            "font": "foo2"
        })

        ecb = MockEnabledCallback()

        action_select, action_morph = KemperActionDefinitions.RIG_SELECT_AND_MORPH_STATE(
            rig = 1,
            rig_off = 2,
            display = display_select, 
            text = "foo",
            id = 67, 
            use_leds = True, 
            enable_callback = ecb,     
            #color_callback
            color = (2, 4, 6),
            #text_callback,
            morph_display = display_morph,
            morph_use_leds = False,
            morph_id = 68,
            morph_only_when_enabled = False
        )

        cb_select = action_select.callback
        cb_morph = action_morph.callback

        self.assertIsInstance(cb_select, BinaryParameterCallback)
        self.assertEqual(cb_select._mapping, KemperMappings.RIG_SELECT(0))

        self.assertIsInstance(cb_morph, KemperMorphCallback)
        self.assertEqual(cb_morph._mapping, KemperMappings.MORPH_PEDAL())
        self.assertEqual(cb_morph._comparison_mode, BinaryParameterCallback.NO_STATE_CHANGE)
        self.assertEqual(cb_morph._led_brightness_off, DEFAULT_LED_BRIGHTNESS_ON)
        self.assertEqual(cb_morph._display_dim_factor_off, DEFAULT_SLOT_DIM_FACTOR_ON)
        self.assertEqual(cb_morph._suppress_send, True)
        
        self.assertEqual(action_select.label, display_select)
        self.assertEqual(action_select.id, 67)
        self.assertEqual(action_select.uses_switch_leds, True)
        self.assertEqual(action_select._enable_callback, ecb)

        self.assertEqual(action_morph.label, display_morph)
        self.assertEqual(action_morph.id, 68)
        self.assertEqual(action_morph.uses_switch_leds, False)
        self.assertNotEqual(action_morph._enable_callback, ecb)


    def test_rig_and_bank_select_and_morph(self):
        display_select = DisplayLabel(layout = {
            "font": "foo"
        })
        display_morph = DisplayLabel(layout = {
            "font": "foo2"
        })

        ecb = MockEnabledCallback()

        action_select, action_morph = KemperActionDefinitions.RIG_AND_BANK_SELECT_AND_MORPH_STATE(
            rig = 1,
            bank = 5, 
            rig_off = 2,
            bank_off = 9,
            display = display_select, 
            text = "foo",
            id = 67, 
            use_leds = True, 
            enable_callback = ecb,     
            #color_callback
            color = (2, 4, 6),
            #text_callback,
            morph_display = display_morph,
            morph_use_leds = False,
            morph_id = 68,
            morph_only_when_enabled = False
        )

        cb_select = action_select.callback
        cb_morph = action_morph.callback

        self.assertIsInstance(cb_select, BinaryParameterCallback)
        self.assertEqual(cb_select._mapping, KemperMappings.BANK_AND_RIG_SELECT(0))

        self.assertIsInstance(cb_morph, KemperMorphCallback)
        self.assertEqual(cb_morph._mapping, KemperMappings.MORPH_PEDAL())
        self.assertEqual(cb_morph._comparison_mode, BinaryParameterCallback.NO_STATE_CHANGE)
        self.assertEqual(cb_morph._led_brightness_off, DEFAULT_LED_BRIGHTNESS_ON)
        self.assertEqual(cb_morph._display_dim_factor_off, DEFAULT_SLOT_DIM_FACTOR_ON)
        self.assertEqual(cb_morph._suppress_send, True)
        
        self.assertEqual(action_select.label, display_select)
        self.assertEqual(action_select.id, 67)
        self.assertEqual(action_select.uses_switch_leds, True)
        self.assertEqual(action_select._enable_callback, ecb)

        self.assertEqual(action_morph.label, display_morph)
        self.assertEqual(action_morph.id, 68)
        self.assertEqual(action_morph.uses_switch_leds, False)
        self.assertNotEqual(action_morph._enable_callback, ecb)