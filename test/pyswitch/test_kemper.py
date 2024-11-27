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
    from lib.pyswitch.clients.kemper import *

    from lib.pyswitch.ui.ui import DisplayElement
    from lib.pyswitch.ui.elements import DisplayLabel, TunerDisplay


class TestKemper(unittest.TestCase):

    def test_nrpn_value(self):
        self.assertEqual(NRPN_VALUE(0), 0)
        self.assertEqual(NRPN_VALUE(0.1), 1638)
        self.assertEqual(NRPN_VALUE(0.5), 8191)
        self.assertEqual(NRPN_VALUE(0.9), 14744)
        self.assertEqual(NRPN_VALUE(1), 16383)


##########################################################################################################


    def test_rig_name_callback(self):
        cb = KemperRigNameCallback()

        self.assertIn(KemperMappings.RIG_NAME(), cb.mappings)

        label = DisplayLabel(
            layout = {
                "font": "foo"
            },
            callback = cb
        )

        mapping = cb.mappings[0]
        mapping.value = "foo"

        cb.update_label(label)

        self.assertEqual(label.text, "foo")


##########################################################################################################


    def test_tuner_display_callback(self):
        element = DisplayElement()

        cb = TunerDisplayCallback(
            splash_default = element
        )

        self.assertIn(KemperMappings.TUNER_MODE_STATE(), cb.mappings)
        
        splash_tuner = cb._splash_tuner

        self.assertIsInstance(splash_tuner, TunerDisplay)

        mapping = cb.mappings[0]

        mapping.value = 0
        self.assertEqual(cb.get_root(), element)

        mapping.value = 1
        self.assertEqual(cb.get_root(), splash_tuner)


    def test_tuner_display_callback_custom(self):
        element = DisplayElement()
        element_2 = DisplayElement()

        cb = TunerDisplayCallback(
            splash_default = element,
            splash_tuner = element_2
        )

        self.assertIn(KemperMappings.TUNER_MODE_STATE(), cb.mappings)
        
        mapping = cb.mappings[0]

        mapping.value = 0
        self.assertEqual(cb.get_root(), element)

        mapping.value = 1
        self.assertEqual(cb.get_root(), element_2)


##########################################################################################################


    def test_effect_slots_consistency(self):
        self.assertEqual(KemperEffectSlot.EFFECT_SLOT_ID_A, 0)
        self.assertEqual(KemperEffectSlot.EFFECT_SLOT_ID_B, 1)
        self.assertEqual(KemperEffectSlot.EFFECT_SLOT_ID_C, 2)
        self.assertEqual(KemperEffectSlot.EFFECT_SLOT_ID_D, 3)
        self.assertEqual(KemperEffectSlot.EFFECT_SLOT_ID_X, 4)
        self.assertEqual(KemperEffectSlot.EFFECT_SLOT_ID_MOD, 5)
        self.assertEqual(KemperEffectSlot.EFFECT_SLOT_ID_DLY, 6)
        self.assertEqual(KemperEffectSlot.EFFECT_SLOT_ID_REV, 7)

        self.assertEqual(len(KemperEffectSlot.CC_EFFECT_SLOT_ENABLE), 8)
        self.assertEqual(len(KemperEffectSlot.NRPN_SLOT_ADDRESS_PAGE), 8)
        self.assertEqual(len(KemperEffectSlot.NRPN_FREEZE_SLOT_PARAMETER_ADDRESSES), 8)


##########################################################################################################


    def test_mappings(self):
        self.assertIn("State", KemperMappings.EFFECT_STATE(KemperEffectSlot.EFFECT_SLOT_ID_A).name)
        self.assertIn("State", KemperMappings.EFFECT_STATE(KemperEffectSlot.EFFECT_SLOT_ID_B).name)
        self.assertIn("State", KemperMappings.EFFECT_STATE(KemperEffectSlot.EFFECT_SLOT_ID_C).name)
        self.assertIn("State", KemperMappings.EFFECT_STATE(KemperEffectSlot.EFFECT_SLOT_ID_D).name)
        self.assertIn("State", KemperMappings.EFFECT_STATE(KemperEffectSlot.EFFECT_SLOT_ID_X).name)
        self.assertIn("State", KemperMappings.EFFECT_STATE(KemperEffectSlot.EFFECT_SLOT_ID_MOD).name)
        self.assertIn("State", KemperMappings.EFFECT_STATE(KemperEffectSlot.EFFECT_SLOT_ID_DLY).name)
        self.assertIn("State", KemperMappings.EFFECT_STATE(KemperEffectSlot.EFFECT_SLOT_ID_REV).name)

        self.assertIn("Type", KemperMappings.EFFECT_TYPE(KemperEffectSlot.EFFECT_SLOT_ID_A).name)
        self.assertIn("Type", KemperMappings.EFFECT_TYPE(KemperEffectSlot.EFFECT_SLOT_ID_B).name)
        self.assertIn("Type", KemperMappings.EFFECT_TYPE(KemperEffectSlot.EFFECT_SLOT_ID_C).name)
        self.assertIn("Type", KemperMappings.EFFECT_TYPE(KemperEffectSlot.EFFECT_SLOT_ID_D).name)
        self.assertIn("Type", KemperMappings.EFFECT_TYPE(KemperEffectSlot.EFFECT_SLOT_ID_X).name)
        self.assertIn("Type", KemperMappings.EFFECT_TYPE(KemperEffectSlot.EFFECT_SLOT_ID_MOD).name)
        self.assertIn("Type", KemperMappings.EFFECT_TYPE(KemperEffectSlot.EFFECT_SLOT_ID_DLY).name)
        self.assertIn("Type", KemperMappings.EFFECT_TYPE(KemperEffectSlot.EFFECT_SLOT_ID_REV).name)

        self.assertIn("Speed", KemperMappings.ROTARY_SPEED(KemperEffectSlot.EFFECT_SLOT_ID_A).name)
        self.assertIn("Speed", KemperMappings.ROTARY_SPEED(KemperEffectSlot.EFFECT_SLOT_ID_B).name)
        self.assertIn("Speed", KemperMappings.ROTARY_SPEED(KemperEffectSlot.EFFECT_SLOT_ID_C).name)
        self.assertIn("Speed", KemperMappings.ROTARY_SPEED(KemperEffectSlot.EFFECT_SLOT_ID_D).name)
        self.assertIn("Speed", KemperMappings.ROTARY_SPEED(KemperEffectSlot.EFFECT_SLOT_ID_X).name)
        self.assertIn("Speed", KemperMappings.ROTARY_SPEED(KemperEffectSlot.EFFECT_SLOT_ID_MOD).name)
        self.assertIn("Speed", KemperMappings.ROTARY_SPEED(KemperEffectSlot.EFFECT_SLOT_ID_DLY).name)
        self.assertIn("Speed", KemperMappings.ROTARY_SPEED(KemperEffectSlot.EFFECT_SLOT_ID_REV).name)

        self.assertIn("Freeze", KemperMappings.FREEZE(KemperEffectSlot.EFFECT_SLOT_ID_A).name)
        self.assertIn("Freeze", KemperMappings.FREEZE(KemperEffectSlot.EFFECT_SLOT_ID_B).name)
        self.assertIn("Freeze", KemperMappings.FREEZE(KemperEffectSlot.EFFECT_SLOT_ID_C).name)
        self.assertIn("Freeze", KemperMappings.FREEZE(KemperEffectSlot.EFFECT_SLOT_ID_D).name)
        self.assertIn("Freeze", KemperMappings.FREEZE(KemperEffectSlot.EFFECT_SLOT_ID_X).name)
        self.assertIn("Freeze", KemperMappings.FREEZE(KemperEffectSlot.EFFECT_SLOT_ID_MOD).name)
        self.assertIn("Freeze", KemperMappings.FREEZE(KemperEffectSlot.EFFECT_SLOT_ID_DLY).name)
        self.assertIn("Freeze", KemperMappings.FREEZE(KemperEffectSlot.EFFECT_SLOT_ID_REV).name)

        self.assertIn("Mix", KemperMappings.DELAY_MIX(KemperEffectSlot.EFFECT_SLOT_ID_A).name)
        self.assertIn("Mix", KemperMappings.DELAY_MIX(KemperEffectSlot.EFFECT_SLOT_ID_B).name)
        self.assertIn("Mix", KemperMappings.DELAY_MIX(KemperEffectSlot.EFFECT_SLOT_ID_C).name)
        self.assertIn("Mix", KemperMappings.DELAY_MIX(KemperEffectSlot.EFFECT_SLOT_ID_D).name)
        self.assertIn("Mix", KemperMappings.DELAY_MIX(KemperEffectSlot.EFFECT_SLOT_ID_X).name)
        self.assertIn("Mix", KemperMappings.DELAY_MIX(KemperEffectSlot.EFFECT_SLOT_ID_MOD).name)
        self.assertIn("Mix", KemperMappings.DELAY_MIX(KemperEffectSlot.EFFECT_SLOT_ID_DLY).name)
        self.assertIn("Mix", KemperMappings.DELAY_MIX(KemperEffectSlot.EFFECT_SLOT_ID_REV).name)

        self.assertIn("Button 1", KemperMappings.EFFECT_BUTTON(1).name)
        self.assertIn("Button 2", KemperMappings.EFFECT_BUTTON(2).name)
        self.assertIn("Button 3", KemperMappings.EFFECT_BUTTON(3).name)
        self.assertIn("Button 4", KemperMappings.EFFECT_BUTTON(4).name)

        self.assertIn("Rig Name", KemperMappings.RIG_NAME().name)

        self.assertIn("Rig Date", KemperMappings.RIG_DATE().name)

        self.assertIn("Tuner", KemperMappings.TUNER_MODE_STATE().name)
        self.assertIn("Tuner Note", KemperMappings.TUNER_NOTE().name)
        self.assertIn("Tuner", KemperMappings.TUNER_DEVIANCE().name)

        self.assertIn("Tap", KemperMappings.TAP_TEMPO().name)

        self.assertIn("Morph Button", KemperMappings.MORPH_BUTTON().name)
        self.assertIn("Morph Pedal", KemperMappings.MORPH_PEDAL().name)

        self.assertIn("Volume", KemperMappings.RIG_VOLUME().name)

        self.assertIn("Amp Name", KemperMappings.AMP_NAME().name)

        self.assertIn("Amp State", KemperMappings.AMP_STATE().name)

        self.assertIn("Cab Name", KemperMappings.CABINET_NAME().name)

        self.assertIn("Cab State", KemperMappings.CABINET_STATE().name)

        self.assertIn("Next", KemperMappings.NEXT_BANK().name)
        self.assertIn("Prev", KemperMappings.PREVIOUS_BANK().name)

        self.assertIn("Rig", KemperMappings.RIG_SELECT(rig = 2).name)

        self.assertIn("Bank", KemperMappings.BANK_AND_RIG_SELECT(rig = 3).name)

        self.assertIn("Sense", KemperMappings.BIDIRECTIONAL_SENSING().name)

        self.assertIn("Tempo", KemperMappings.TEMPO_DISPLAY().name)
