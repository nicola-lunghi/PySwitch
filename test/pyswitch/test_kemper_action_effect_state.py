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
    from lib.pyswitch.clients.kemper import KemperMappings, KemperEffectSlot
    from lib.pyswitch.ui.elements import DisplayLabel
    
    from .mocks_appl import *
    from .mocks_callback import *

    from lib.pyswitch.clients.kemper.actions.effect_state import *



class TestKemperActionEffectState(unittest.TestCase):

    def test_effect_state(self):
        display = DisplayLabel(layout = {
            "font": "foo"
        })

        ecb = MockEnabledCallback()

        action = EFFECT_STATE(
            KemperEffectSlot.EFFECT_SLOT_ID_C, 
            display = display,
            mode = PushButtonAction.LATCH, 
            id = 45, 
            use_leds = True, 
            enable_callback = ecb
        )

        cb = action.callback
        self.assertIsInstance(cb, KemperEffectEnableCallback)
        self.assertEqual(cb.mapping, KemperMappings.EFFECT_STATE(KemperEffectSlot.EFFECT_SLOT_ID_C))
        self.assertEqual(cb.mapping_fxtype, KemperMappings.EFFECT_TYPE(KemperEffectSlot.EFFECT_SLOT_ID_C))

        self.assertIsInstance(action, PushButtonAction)

        self.assertEqual(cb.mapping_fxtype, KemperMappings.EFFECT_TYPE(KemperEffectSlot.EFFECT_SLOT_ID_C))
        
        self.assertEqual(action.label, display)
        self.assertEqual(action.id, 45)
        self.assertEqual(action.uses_switch_leds, True)
        self.assertEqual(action._Action__enable_callback, ecb)
        self.assertEqual(action._PushButtonAction__mode, PushButtonAction.LATCH)


    def test_effect_categories(self):
        cb = KemperEffectEnableCallback(KemperEffectSlot.EFFECT_SLOT_ID_DLY)

        # None
        self.assertEqual(cb.get_effect_category(0), KemperEffectEnableCallback.CATEGORY_NONE)

        # Wah (and some pitch)
        for i in range(1, 10):
            self.assertEqual(cb.get_effect_category(i), KemperEffectEnableCallback.CATEGORY_WAH)

        self.assertEqual(cb.get_effect_category(11), KemperEffectEnableCallback.CATEGORY_PITCH)
        self.assertEqual(cb.get_effect_category(12), KemperEffectEnableCallback.CATEGORY_WAH)
        self.assertEqual(cb.get_effect_category(13), KemperEffectEnableCallback.CATEGORY_PITCH)

        # Dist
        for i in range(17, 42):
            self.assertEqual(cb.get_effect_category(i), KemperEffectEnableCallback.CATEGORY_DISTORTION)

        # Comp
        for i in range(49, 56):
            self.assertEqual(cb.get_effect_category(i), KemperEffectEnableCallback.CATEGORY_COMPRESSOR)

        # Noise Gate
        for i in range(57, 58):
            self.assertEqual(cb.get_effect_category(i), KemperEffectEnableCallback.CATEGORY_NOISE_GATE)

        # Space
        self.assertEqual(cb.get_effect_category(64), KemperEffectEnableCallback.CATEGORY_SPACE)

        # Chorus
        for i in range(65, 71):
            self.assertEqual(cb.get_effect_category(i), KemperEffectEnableCallback.CATEGORY_CHORUS)

        # Phaser / Flanger
        for i in range(81, 91):
            self.assertEqual(cb.get_effect_category(i), KemperEffectEnableCallback.CATEGORY_PHASER_FLANGER)

        # EQ
        for i in range(97, 104):
            self.assertEqual(cb.get_effect_category(i), KemperEffectEnableCallback.CATEGORY_EQUALIZER)

        # Boost
        for i in range(113, 116):
            self.assertEqual(cb.get_effect_category(i), KemperEffectEnableCallback.CATEGORY_BOOSTER)

        # Looper
        for i in range(121, 123):
            self.assertEqual(cb.get_effect_category(i), KemperEffectEnableCallback.CATEGORY_LOOPER)

        # Pitch
        for i in range(129, 132):
            self.assertEqual(cb.get_effect_category(i), KemperEffectEnableCallback.CATEGORY_PITCH)

        # Dual
        for i in range(137, 140):
            self.assertEqual(cb.get_effect_category(i), KemperEffectEnableCallback.CATEGORY_DUAL)

        # Delay
        for i in range(145, 166):
            self.assertEqual(cb.get_effect_category(i), KemperEffectEnableCallback.CATEGORY_DELAY)

        # Rev
        for i in range(177, 193):
            self.assertEqual(cb.get_effect_category(i), KemperEffectEnableCallback.CATEGORY_REVERB)


    def test_type_colors(self):
        # All types have to be mapped
        cb = KemperEffectEnableCallback(KemperEffectSlot.EFFECT_SLOT_ID_DLY)

        cb.get_effect_category_color(KemperEffectEnableCallback.CATEGORY_WAH, 0)
        cb.get_effect_category_color(KemperEffectEnableCallback.CATEGORY_DISTORTION, 0)
        cb.get_effect_category_color(KemperEffectEnableCallback.CATEGORY_COMPRESSOR, 0)
        cb.get_effect_category_color(KemperEffectEnableCallback.CATEGORY_NOISE_GATE, 0)
        cb.get_effect_category_color(KemperEffectEnableCallback.CATEGORY_SPACE, 0)
        cb.get_effect_category_color(KemperEffectEnableCallback.CATEGORY_CHORUS, 0)
        cb.get_effect_category_color(KemperEffectEnableCallback.CATEGORY_PHASER_FLANGER, 0)
        cb.get_effect_category_color(KemperEffectEnableCallback.CATEGORY_EQUALIZER, 0)
        cb.get_effect_category_color(KemperEffectEnableCallback.CATEGORY_BOOSTER, 0)
        cb.get_effect_category_color(KemperEffectEnableCallback.CATEGORY_LOOPER, 0)
        cb.get_effect_category_color(KemperEffectEnableCallback.CATEGORY_PITCH, 0)
        cb.get_effect_category_color(KemperEffectEnableCallback.CATEGORY_DUAL, 0)
        cb.get_effect_category_color(KemperEffectEnableCallback.CATEGORY_DELAY, 0)
        cb.get_effect_category_color(KemperEffectEnableCallback.CATEGORY_REVERB, 0)

    def test_color_override(self):
        cb = KemperEffectEnableCallback(
            slot_id = KemperEffectSlot.EFFECT_SLOT_ID_DLY,
            color = (6, 7, 8)
        )

        self.assertEqual(cb.get_effect_category_color(KemperEffectEnableCallback.CATEGORY_WAH, 0), (6, 7, 8))
        self.assertEqual(cb.get_effect_category_color(KemperEffectEnableCallback.CATEGORY_COMPRESSOR, 0), (6, 7, 8))
        self.assertEqual(cb.get_effect_category_color(KemperEffectEnableCallback.CATEGORY_REVERB, 0), (6, 7, 8))
        self.assertEqual(cb.get_effect_category_color("anyvalue", 0), (6, 7, 8))        

    def test_text_override(self):
        cb = KemperEffectEnableCallback(
            slot_id = KemperEffectSlot.EFFECT_SLOT_ID_DLY,
            text = "foo"
        )

        self.assertEqual(cb.get_effect_category_text(KemperEffectEnableCallback.CATEGORY_WAH, 0), "foo")
        self.assertEqual(cb.get_effect_category_text(KemperEffectEnableCallback.CATEGORY_COMPRESSOR, 0), "foo")
        self.assertEqual(cb.get_effect_category_text(KemperEffectEnableCallback.CATEGORY_REVERB, 0), "foo")
        self.assertEqual(cb.get_effect_category_text("anyvalue", 0), "foo")

    def test_show_slot_names(self):
        self._test_show_slot_names(KemperEffectSlot.EFFECT_SLOT_ID_A, "A Wah")
        self._test_show_slot_names(KemperEffectSlot.EFFECT_SLOT_ID_B, "B Wah")
        self._test_show_slot_names(KemperEffectSlot.EFFECT_SLOT_ID_C, "C Wah")
        self._test_show_slot_names(KemperEffectSlot.EFFECT_SLOT_ID_D, "D Wah")

        self._test_show_slot_names(KemperEffectSlot.EFFECT_SLOT_ID_X, "X Wah")
        self._test_show_slot_names(KemperEffectSlot.EFFECT_SLOT_ID_MOD, "MOD Wah")
        self._test_show_slot_names(KemperEffectSlot.EFFECT_SLOT_ID_DLY, "DLY Wah")
        self._test_show_slot_names(KemperEffectSlot.EFFECT_SLOT_ID_REV, "REV Wah")

    def _test_show_slot_names(self, slot_id, exp_text):
        cb = KemperEffectEnableCallback(
            slot_id = slot_id,
            show_slot_names = True
        )

        self.assertEqual(cb.get_effect_category_text(KemperEffectEnableCallback.CATEGORY_WAH, 0), exp_text)
        
    def test_type_names(self):
        # All types have to be mapped
        cb = KemperEffectEnableCallback(KemperEffectSlot.EFFECT_SLOT_ID_DLY)

        cb.get_effect_category_text(KemperEffectEnableCallback.CATEGORY_WAH, 0)
        cb.get_effect_category_text(KemperEffectEnableCallback.CATEGORY_DISTORTION, 0)
        cb.get_effect_category_text(KemperEffectEnableCallback.CATEGORY_COMPRESSOR, 0)
        cb.get_effect_category_text(KemperEffectEnableCallback.CATEGORY_NOISE_GATE, 0)
        cb.get_effect_category_text(KemperEffectEnableCallback.CATEGORY_SPACE, 0)
        cb.get_effect_category_text(KemperEffectEnableCallback.CATEGORY_CHORUS, 0)
        cb.get_effect_category_text(KemperEffectEnableCallback.CATEGORY_PHASER_FLANGER, 0)
        cb.get_effect_category_text(KemperEffectEnableCallback.CATEGORY_EQUALIZER, 0)
        cb.get_effect_category_text(KemperEffectEnableCallback.CATEGORY_BOOSTER, 0)
        cb.get_effect_category_text(KemperEffectEnableCallback.CATEGORY_LOOPER, 0)
        cb.get_effect_category_text(KemperEffectEnableCallback.CATEGORY_PITCH, 0)
        cb.get_effect_category_text(KemperEffectEnableCallback.CATEGORY_DUAL, 0)
        cb.get_effect_category_text(KemperEffectEnableCallback.CATEGORY_DELAY, 0)
        cb.get_effect_category_text(KemperEffectEnableCallback.CATEGORY_REVERB, 0)


