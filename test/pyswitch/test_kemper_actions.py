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
    from lib.pyswitch.controller.callbacks import BinaryParameterCallback
    from lib.pyswitch.misc import Updater
    
    from .mocks_appl import *
    from .mocks_callback import *


class MockController2(Updater):
    def __init__(self):
        Updater.__init__(self)
        self.client = MockClient()
        self.config = {}


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

        self.assertEqual(cb._BinaryParameterCallback__mapping, mapping_1)
        self.assertEqual(cb._BinaryParameterCallback__value_enable, 3)
        self.assertEqual(cb._BinaryParameterCallback__value_disable, 5)
        self.assertEqual(cb._BinaryParameterCallback__reference_value, 6)
        self.assertEqual(cb._BinaryParameterCallback__text, "foo")
        self.assertEqual(cb._BinaryParameterCallback__color, (2, 3, 4))
        self.assertEqual(cb._BinaryParameterCallback__comparison_mode, BinaryParameterCallback.LESS)

        self.assertEqual(action.label, display)
        self.assertEqual(action.id, 45)
        self.assertEqual(action.uses_switch_leds, True)
        self.assertEqual(action._Action__enable_callback, ecb)


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
        self.assertEqual(action._Action__enable_callback, ecb)
        self.assertEqual(action._PushButtonAction__mode, PushButtonAction.LATCH)


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

        self.assertEqual(cb._BinaryParameterCallback__mapping, KemperMappings.TAP_TEMPO())
        self.assertEqual(cb._BinaryParameterCallback__text, "Tap")
        self.assertEqual(cb._BinaryParameterCallback__color, (4, 5, 6))

        self.assertEqual(action.label, display)
        self.assertEqual(action.id, 67)
        self.assertEqual(action.uses_switch_leds, True)
        self.assertEqual(action._Action__enable_callback, ecb)


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

        self.assertEqual(cb._BinaryParameterCallback__mapping, KemperMappings.EFFECT_BUTTON(num))
        self.assertEqual(cb._BinaryParameterCallback__text, exp_text)
        self.assertEqual(cb._BinaryParameterCallback__color, (4, 5, 6))

        self.assertEqual(action.label, display)
        self.assertEqual(action.id, 67)
        self.assertEqual(action.uses_switch_leds, True)
        self.assertEqual(action._Action__enable_callback, ecb)


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

        self.assertEqual(cb._BinaryParameterCallback__mapping, KemperMappings.MORPH_BUTTON())
        self.assertEqual(cb._BinaryParameterCallback__text, "foo")
        self.assertEqual(cb._BinaryParameterCallback__color, (3, 4, 5))
        self.assertEqual(cb._BinaryParameterCallback__value_enable, 1)
        self.assertEqual(cb._BinaryParameterCallback__value_disable, 0)

        self.assertEqual(action.label, display)
        self.assertEqual(action.id, 67)
        self.assertEqual(action.uses_switch_leds, True)
        self.assertEqual(action._Action__enable_callback, ecb)
        self.assertEqual(action._PushButtonAction__mode, PushButtonAction.MOMENTARY)


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

        self.assertEqual(cb._BinaryParameterCallback__mapping, KemperMappings.MORPH_BUTTON())
        self.assertEqual(cb._BinaryParameterCallback__text, "foo")
        self.assertEqual(cb._BinaryParameterCallback__value_enable, 1)
        self.assertEqual(cb._BinaryParameterCallback__value_disable, 0)

        self.assertEqual(action.label, display)
        self.assertEqual(action.id, 67)
        self.assertEqual(action.uses_switch_leds, True)
        self.assertEqual(action._Action__enable_callback, ecb)
        self.assertEqual(action._PushButtonAction__mode, PushButtonAction.MOMENTARY)


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

        appl = MockController2()
        action.init(appl, None)

        cb = action.callback
        self.assertIsInstance(cb, KemperMorphCallback)
        self.assertIsInstance(action, PushButtonAction)

        self.assertEqual(cb._BinaryParameterCallback__mapping, KemperMappings.MORPH_PEDAL())
        self.assertEqual(cb._BinaryParameterCallback__text, "foo")
        self.assertEqual(cb._BinaryParameterCallback__comparison_mode, BinaryParameterCallback.NO_STATE_CHANGE)
        self.assertEqual(cb._led_brightness_off, 0.3)

        self.assertEqual(cb._BinaryParameterCallback__display_dim_factor_off, 1)
        self.assertEqual(cb._KemperMorphCallback__suppress_send, True)
        
        self.assertEqual(action.label, display)
        self.assertEqual(action.id, 67)
        self.assertEqual(action.uses_switch_leds, True)
        self.assertEqual(action._Action__enable_callback, ecb)


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

        self.assertEqual(cb._BinaryParameterCallback__mapping, KemperMappings.RIG_VOLUME())
        self.assertEqual(cb._BinaryParameterCallback__text, "foo")
        self.assertEqual(cb._BinaryParameterCallback__value_enable, exp_value_enable)
        self.assertEqual(cb._BinaryParameterCallback__value_disable, exp_value_disable)
        self.assertEqual(cb._BinaryParameterCallback__color, (4, 5, 6))

        self.assertEqual(action.label, display)
        self.assertEqual(action.id, 67)
        self.assertEqual(action.uses_switch_leds, True)
        self.assertEqual(action._Action__enable_callback, ecb)
        self.assertEqual(action._PushButtonAction__mode, PushButtonAction.LATCH)


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

        appl = MockController2()
        action_select.init(appl, None)
        action_morph.init(appl, None)

        cb_select = action_select.callback
        cb_morph = action_morph.callback

        self.assertIsInstance(cb_select, BinaryParameterCallback)
        self.assertEqual(cb_select._BinaryParameterCallback__mapping, KemperMappings.RIG_SELECT(0))

        self.assertIsInstance(cb_morph, KemperMorphCallback)
        self.assertEqual(cb_morph._BinaryParameterCallback__mapping, KemperMappings.MORPH_PEDAL())
        self.assertEqual(cb_morph._BinaryParameterCallback__comparison_mode, BinaryParameterCallback.NO_STATE_CHANGE)
        self.assertEqual(cb_morph._led_brightness_off, 0.3)
        self.assertEqual(cb_morph._BinaryParameterCallback__display_dim_factor_off, 1)
        self.assertEqual(cb_morph._KemperMorphCallback__suppress_send, True)
        
        self.assertEqual(action_select.label, display_select)
        self.assertEqual(action_select.id, 67)
        self.assertEqual(action_select.uses_switch_leds, True)
        self.assertEqual(action_select._Action__enable_callback, ecb)

        self.assertEqual(action_morph.label, display_morph)
        self.assertEqual(action_morph.id, 68)
        self.assertEqual(action_morph.uses_switch_leds, False)
        self.assertNotEqual(action_morph._Action__enable_callback, ecb)


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

        appl = MockController2()
        action_select.init(appl, None)
        action_morph.init(appl, None)

        cb_select = action_select.callback
        cb_morph = action_morph.callback

        self.assertIsInstance(cb_select, BinaryParameterCallback)
        self.assertEqual(cb_select._BinaryParameterCallback__mapping, KemperMappings.BANK_AND_RIG_SELECT(0))

        self.assertIsInstance(cb_morph, KemperMorphCallback)
        self.assertEqual(cb_morph._BinaryParameterCallback__mapping, KemperMappings.MORPH_PEDAL())
        self.assertEqual(cb_morph._BinaryParameterCallback__comparison_mode, BinaryParameterCallback.NO_STATE_CHANGE)
        self.assertEqual(cb_morph._led_brightness_off, 0.3)
        self.assertEqual(cb_morph._BinaryParameterCallback__display_dim_factor_off, 1)
        self.assertEqual(cb_morph._KemperMorphCallback__suppress_send, True)
        
        self.assertEqual(action_select.label, display_select)
        self.assertEqual(action_select.id, 67)
        self.assertEqual(action_select.uses_switch_leds, True)
        self.assertEqual(action_select._Action__enable_callback, ecb)

        self.assertEqual(action_morph.label, display_morph)
        self.assertEqual(action_morph.id, 68)
        self.assertEqual(action_morph.uses_switch_leds, False)
        self.assertNotEqual(action_morph._Action__enable_callback, ecb)