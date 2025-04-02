import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

# Import subject under test
with patch.dict(sys.modules, {
    "micropython": MockMicropython,
    "displayio": MockDisplayIO(),
    "adafruit_display_text": MockAdafruitDisplayText(),
    #"adafruit_midi": MockAdafruitMIDI(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "adafruit_midi.program_change": MockAdafruitMIDIProgramChange(),
    "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
    "gc": MockGC()
}):
    from lib.pyswitch.clients.kemper import *
    
    from lib.pyswitch.misc import Updater

    from .mocks_appl import MockClient
    from lib.pyswitch.clients.kemper.mappings.select import *
    from lib.pyswitch.clients.kemper.mappings.rotary import *
    from lib.pyswitch.clients.kemper.mappings.freeze import *
    from lib.pyswitch.clients.kemper.mappings.effects import *
    from lib.pyswitch.clients.kemper.mappings.rig import *
    from lib.pyswitch.clients.kemper.mappings.bank import *
    from lib.pyswitch.clients.kemper.mappings.tempo import *
    from lib.pyswitch.clients.kemper.mappings.tempo_bpm import *
    from lib.pyswitch.clients.kemper.mappings.morph import *
    from lib.pyswitch.clients.kemper.mappings.amp import *
    from lib.pyswitch.clients.kemper.mappings.cabinet import *
    from lib.pyswitch.clients.kemper.mappings.looper import *
    from lib.pyswitch.clients.kemper.mappings.pedals import *


class TestKemper(unittest.TestCase):

    def test_nrpn_value(self):
        self.assertEqual(NRPN_VALUE(0), 0)
        self.assertEqual(NRPN_VALUE(0.1), 1638)
        self.assertEqual(NRPN_VALUE(0.5), 8191)
        self.assertEqual(NRPN_VALUE(0.9), 14744)
        self.assertEqual(NRPN_VALUE(1), 16383)


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
        self.assertIn("State A", KemperMappings.EFFECT_STATE(KemperEffectSlot.EFFECT_SLOT_ID_A).name)
        self.assertIn("State B", KemperMappings.EFFECT_STATE(KemperEffectSlot.EFFECT_SLOT_ID_B).name)
        self.assertIn("State C", KemperMappings.EFFECT_STATE(KemperEffectSlot.EFFECT_SLOT_ID_C).name)
        self.assertIn("State D", KemperMappings.EFFECT_STATE(KemperEffectSlot.EFFECT_SLOT_ID_D).name)
        self.assertIn("State X", KemperMappings.EFFECT_STATE(KemperEffectSlot.EFFECT_SLOT_ID_X).name)
        self.assertIn("State MOD", KemperMappings.EFFECT_STATE(KemperEffectSlot.EFFECT_SLOT_ID_MOD).name)
        self.assertIn("State DLY", KemperMappings.EFFECT_STATE(KemperEffectSlot.EFFECT_SLOT_ID_DLY).name)
        self.assertIn("State REV", KemperMappings.EFFECT_STATE(KemperEffectSlot.EFFECT_SLOT_ID_REV).name)

        self.assertIn("Type A", KemperMappings.EFFECT_TYPE(KemperEffectSlot.EFFECT_SLOT_ID_A).name)
        self.assertIn("Type B", KemperMappings.EFFECT_TYPE(KemperEffectSlot.EFFECT_SLOT_ID_B).name)
        self.assertIn("Type C", KemperMappings.EFFECT_TYPE(KemperEffectSlot.EFFECT_SLOT_ID_C).name)
        self.assertIn("Type D", KemperMappings.EFFECT_TYPE(KemperEffectSlot.EFFECT_SLOT_ID_D).name)
        self.assertIn("Type X", KemperMappings.EFFECT_TYPE(KemperEffectSlot.EFFECT_SLOT_ID_X).name)
        self.assertIn("Type MOD", KemperMappings.EFFECT_TYPE(KemperEffectSlot.EFFECT_SLOT_ID_MOD).name)
        self.assertIn("Type DLY", KemperMappings.EFFECT_TYPE(KemperEffectSlot.EFFECT_SLOT_ID_DLY).name)
        self.assertIn("Type REV", KemperMappings.EFFECT_TYPE(KemperEffectSlot.EFFECT_SLOT_ID_REV).name)

        self.assertIn("Speed A", MAPPING_ROTARY_SPEED(KemperEffectSlot.EFFECT_SLOT_ID_A).name)
        self.assertIn("Speed B", MAPPING_ROTARY_SPEED(KemperEffectSlot.EFFECT_SLOT_ID_B).name)
        self.assertIn("Speed C", MAPPING_ROTARY_SPEED(KemperEffectSlot.EFFECT_SLOT_ID_C).name)
        self.assertIn("Speed D", MAPPING_ROTARY_SPEED(KemperEffectSlot.EFFECT_SLOT_ID_D).name)
        self.assertIn("Speed X", MAPPING_ROTARY_SPEED(KemperEffectSlot.EFFECT_SLOT_ID_X).name)
        self.assertIn("Speed MOD", MAPPING_ROTARY_SPEED(KemperEffectSlot.EFFECT_SLOT_ID_MOD).name)
        self.assertIn("Speed DLY", MAPPING_ROTARY_SPEED(KemperEffectSlot.EFFECT_SLOT_ID_DLY).name)
        self.assertIn("Speed REV", MAPPING_ROTARY_SPEED(KemperEffectSlot.EFFECT_SLOT_ID_REV).name)

        self.assertIn("Freeze A", MAPPING_FREEZE(KemperEffectSlot.EFFECT_SLOT_ID_A).name)
        self.assertIn("Freeze B", MAPPING_FREEZE(KemperEffectSlot.EFFECT_SLOT_ID_B).name)
        self.assertIn("Freeze C", MAPPING_FREEZE(KemperEffectSlot.EFFECT_SLOT_ID_C).name)
        self.assertIn("Freeze D", MAPPING_FREEZE(KemperEffectSlot.EFFECT_SLOT_ID_D).name)
        self.assertIn("Freeze X", MAPPING_FREEZE(KemperEffectSlot.EFFECT_SLOT_ID_X).name)
        self.assertIn("Freeze MOD", MAPPING_FREEZE(KemperEffectSlot.EFFECT_SLOT_ID_MOD).name)
        self.assertIn("Freeze DLY", MAPPING_FREEZE(KemperEffectSlot.EFFECT_SLOT_ID_DLY).name)
        self.assertIn("Freeze REV", MAPPING_FREEZE(KemperEffectSlot.EFFECT_SLOT_ID_REV).name)

        self.assertIn("Mix A", MAPPING_DLY_REV_MIX(KemperEffectSlot.EFFECT_SLOT_ID_A).name)
        self.assertIn("Mix B", MAPPING_DLY_REV_MIX(KemperEffectSlot.EFFECT_SLOT_ID_B).name)
        self.assertIn("Mix C", MAPPING_DLY_REV_MIX(KemperEffectSlot.EFFECT_SLOT_ID_C).name)
        self.assertIn("Mix D", MAPPING_DLY_REV_MIX(KemperEffectSlot.EFFECT_SLOT_ID_D).name)
        self.assertIn("Mix X", MAPPING_DLY_REV_MIX(KemperEffectSlot.EFFECT_SLOT_ID_X).name)
        self.assertIn("Mix MOD", MAPPING_DLY_REV_MIX(KemperEffectSlot.EFFECT_SLOT_ID_MOD).name)
        self.assertIn("Mix DLY", MAPPING_DLY_REV_MIX(KemperEffectSlot.EFFECT_SLOT_ID_DLY).name)
        self.assertIn("Mix REV", MAPPING_DLY_REV_MIX(KemperEffectSlot.EFFECT_SLOT_ID_REV).name)

        self.assertIn("Button 1", MAPPING_EFFECT_BUTTON(1).name)
        self.assertIn("Button 2", MAPPING_EFFECT_BUTTON(2).name)
        self.assertIn("Button 3", MAPPING_EFFECT_BUTTON(3).name)
        self.assertIn("Button 4", MAPPING_EFFECT_BUTTON(4).name)

        self.assertIn("Rig Name", KemperMappings.RIG_NAME().name)
        self.assertIn("Rig ID", KemperMappings.RIG_ID().name)
        self.assertIn("Rig Date", KemperMappings.RIG_DATE().name)
        
        self.assertIn("Tuner", KemperMappings.TUNER_MODE_STATE().name)
        self.assertIn("Tuner Note", KemperMappings.TUNER_NOTE().name)
        self.assertIn("Tuner", KemperMappings.TUNER_DEVIANCE().name)

        self.assertIn("Morph Button", MAPPING_MORPH_BUTTON().name)
        self.assertIn("Morph", MAPPING_MORPH_PEDAL().name)

        self.assertIn("RigVol", MAPPING_RIG_VOLUME().name)

        self.assertIn("Amp Name", MAPPING_AMP_NAME().name)
        self.assertIn("Amp State", MAPPING_AMP_STATE().name)
        self.assertIn("Gain", MAPPING_AMP_GAIN().name)

        self.assertIn("Cab Name", MAPPING_CABINET_NAME().name)
        self.assertIn("Cab State", MAPPING_CABINET_STATE().name)
        
        self.assertIn("Next", MAPPING_NEXT_BANK().name)
        self.assertIn("Prev", MAPPING_PREVIOUS_BANK().name)

        self.assertIn("Rig", MAPPING_RIG_SELECT(rig = 2).name)

        self.assertIn("Bank", MAPPING_BANK_AND_RIG_SELECT(rig = 3).name)

        self.assertIn("Sense", KemperMappings.BIDIRECTIONAL_SENSING().name)

        self.assertIn("Tempo", MAPPING_TEMPO_DISPLAY().name)
        self.assertIn("Tap", MAPPING_TAP_TEMPO().name)
        self.assertIn("BPM", MAPPING_TEMPO_BPM().name)

        self.assertIn("Freeze", MAPPING_FREEZE_ALL_GLOBAL().name)

        self.assertIn("Comment", MAPPING_RIG_COMMENT().name)

        self.assertIn("Loop", MAPPING_LOOPER_REC_PLAY_OVERDUB().name)
        self.assertIn("Loop", MAPPING_LOOPER_STOP().name)
        self.assertIn("Loop", MAPPING_LOOPER_TRIGGER().name)
        self.assertIn("Loop", MAPPING_LOOPER_REVERSE().name)
        self.assertIn("Loop", MAPPING_LOOPER_HALF_SPEED().name)
        self.assertIn("Loop", MAPPING_LOOPER_CANCEL().name)
        self.assertIn("Loop", MAPPING_LOOPER_ERASE().name)

        self.assertIn("Vol", MAPPING_VOLUME_PEDAL().name)
        self.assertIn("Wah", MAPPING_WAH_PEDAL().name)
        self.assertIn("Pitch", MAPPING_PITCH_PEDAL().name)

        self.assertIn("DlMix", MAPPING_DELAY_MIX_PEDAL().name)   
        self.assertIn("Feed", MAPPING_DELAY_FEEDBACK_PEDAL().name)   
        self.assertIn("RvMix", MAPPING_REVERB_MIX_PEDAL().name)
        self.assertIn("RvTime", MAPPING_REVERB_TIME_PEDAL().name)
        self.assertIn("OutVol", MAPPING_VOLUME_OUTPUT_PEDAL().name)
