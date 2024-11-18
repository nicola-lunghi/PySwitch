import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

with patch.dict(sys.modules, {
    "micropython": MockMicropython,
    "displayio": MockDisplayIO(),
    "adafruit_display_text": MockAdafruitDisplayText(),
    "usb_midi": MockUsbMidi(),
    "adafruit_midi": MockAdafruitMIDI(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "adafruit_midi.program_change": MockAdafruitMIDIProgramChange(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
    "gc": MockGC()
}):
    from adafruit_midi.system_exclusive import SystemExclusive

    from lib.pyswitch.ui.ui import DisplayBounds
    from lib.pyswitch.ui.elements import TunerDisplay, DisplayLabel
    from lib.pyswitch.ui.UiController import UiController

    from .mocks_appl import *
    from .mocks_ui import MockDisplayDriver, MockFontLoader, MockSplashCallback
    from lib.pyswitch.misc import Colors



TUNER_NOTE_NAMES = TunerDisplay._TUNER_NOTE_NAMES


class TestTunerDisplay(unittest.TestCase):

    def test_note_name_definition(self):
        # We do not check the half steps because there are different definitions possible for that.
        # At least the notes of C major shoulb be the same (since the H is abandoned in germany, too!)
        self.assertEqual(TUNER_NOTE_NAMES[0], "C")
        self.assertEqual(TUNER_NOTE_NAMES[2], "D")
        self.assertEqual(TUNER_NOTE_NAMES[4], "E")
        self.assertEqual(TUNER_NOTE_NAMES[5], "F")
        self.assertEqual(TUNER_NOTE_NAMES[7], "G")
        self.assertEqual(TUNER_NOTE_NAMES[9], "A")
        self.assertEqual(TUNER_NOTE_NAMES[11], "B")


    def test_note_only(self):
        self._do_test()


    def test_with_deviance(self):
        self._do_test(0, -1, TunerDisplay.COLOR_OUT_OF_TUNE)
        self._do_test(4096, -0.5, TunerDisplay.COLOR_OUT_OF_TUNE)
        self._do_test(8193, 0, TunerDisplay.COLOR_IN_TUNE)
        self._do_test(12288, 0.5, TunerDisplay.COLOR_OUT_OF_TUNE)
        self._do_test(16383, 1, TunerDisplay.COLOR_OUT_OF_TUNE)


    ##################################################################################################################


    def _do_test(self, deviance_value = None, deviance_pos = None, exp_color = None, deviance_tolerance = 0.15):
        self._do_test_all_notes(0, deviance_value, deviance_pos, exp_color, deviance_tolerance)
        self._do_test_all_notes(12, deviance_value, deviance_pos, exp_color, deviance_tolerance)
        self._do_test_all_notes(24, deviance_value, deviance_pos, exp_color, deviance_tolerance)
        self._do_test_all_notes(12*12, deviance_value, deviance_pos, exp_color, deviance_tolerance)


    def _do_test_all_notes(self, offset, deviance_value, deviance_pos, exp_color, deviance_tolerance):
        self._test_scenario(offset + 0, TUNER_NOTE_NAMES[0], deviance_value, deviance_pos, 1, exp_color, deviance_tolerance)
        self._test_scenario(offset + 1, TUNER_NOTE_NAMES[1], deviance_value, deviance_pos, 2, exp_color, deviance_tolerance)
        self._test_scenario(offset + 2, TUNER_NOTE_NAMES[2], deviance_value, deviance_pos, 3, exp_color, deviance_tolerance)
        self._test_scenario(offset + 3, TUNER_NOTE_NAMES[3], deviance_value, deviance_pos, 1.1, exp_color, deviance_tolerance)
        self._test_scenario(offset + 4, TUNER_NOTE_NAMES[4], deviance_value, deviance_pos, 0.1, exp_color, deviance_tolerance)
        self._test_scenario(offset + 5, TUNER_NOTE_NAMES[5], deviance_value, deviance_pos, 1, exp_color, deviance_tolerance)
        self._test_scenario(offset + 6, TUNER_NOTE_NAMES[6], deviance_value, deviance_pos, 1, exp_color, deviance_tolerance)
        self._test_scenario(offset + 7, TUNER_NOTE_NAMES[7], deviance_value, deviance_pos, 0.5, exp_color, deviance_tolerance)
        self._test_scenario(offset + 8, TUNER_NOTE_NAMES[8], deviance_value, deviance_pos, -1000, exp_color, deviance_tolerance)
        self._test_scenario(offset + 9, TUNER_NOTE_NAMES[9], deviance_value, deviance_pos, 10, exp_color, deviance_tolerance)
        self._test_scenario(offset + 10, TUNER_NOTE_NAMES[10], deviance_value, deviance_pos, 11, exp_color, deviance_tolerance)
        self._test_scenario(offset + 11, TUNER_NOTE_NAMES[11], deviance_value, deviance_pos, 1000, exp_color, deviance_tolerance)


    def _test_scenario(self, note_value, note_text, deviance_value, deviance_pos, deviance_zoom, exp_color, deviance_tolerance):
        period = MockPeriodCounter()

        mapping_1 = MockParameterMapping(
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0x09]
            )
        )

        mapping_2 = None
        if deviance_value != None:
            mapping_2 = MockParameterMapping(
                response = SystemExclusive(
                    manufacturer_id = [0x00, 0x10, 0x20],
                    data = [0x00, 0x00, 0x10]
                )
            )

        deviance_width = 4

        display = TunerDisplay(
            mapping_note = mapping_1,
            mapping_deviance = mapping_2,
            bounds = DisplayBounds(20, 33, 444, 555),
            layout = {
                "font": "foo"
            },
            deviance_height = 44,
            deviance_width = deviance_width,
            deviance_zoom = deviance_zoom,
            scale = 2.33
        )

        self.assertIsInstance(display.label_note, DisplayLabel)
        self.assertEqual(len(display.children), 1 if deviance_value == None else 2)
        self.assertEqual(display.children[0], display.label_note)
        self.assertEqual(display.label_note.bounds, DisplayBounds(20, 33, 444, 555))

        if deviance_value != None:
            self.assertEqual(display.children[1], display.deviance)
            self.assertEqual(display.deviance.bounds, DisplayBounds(20, 33 + 555 - 44, 444, 44))

        ui = UiController(
            display_driver = MockDisplayDriver(init = True), 
            font_loader = MockFontLoader(), 
            splash_callback = MockSplashCallback(output = display)
        )
        
        protocol = MockBidirectionalProtocol()
        protocol.outputs_is_bidirectional = [
            {
                "mapping": mapping_1,
                "result": True
            },
            {
                "mapping": mapping_2,
                "result": True
            }
        ]
        protocol.outputs_feedback_value = [
            {
                "mapping": mapping_1,
                "result": True
            },
            {
                "mapping": mapping_2,
                "result": True
            }
        ]

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            protocol = protocol,
            midi = MockMidiController(),
            period_counter = period,
            ui = ui
        )

        answer_msg_1 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0x09, 0x44]
        )

        answer_msg_2 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0x09, 0x45]
        )

        # Build scene:
        # Step 1: Not exceeded
        def prep1():
            self.assertEqual(display.label_note._label.scale, 2.33)
            period.exceed_next_time = True
            
        def eval1():
            self.assertEqual(len(appl._midi.messages_sent), 0)
            return True

        # Step 2: Exceeded the first time
        def prep2():
            period.exceed_next_time = True

            appl._midi.next_receive_messages = [
                answer_msg_1,
                answer_msg_2
            ]
            mapping_1.outputs_parse = [
                {
                    "message": answer_msg_1,
                    "value": note_value
                }
            ]
            if mapping_2:
                mapping_2.outputs_parse = [
                    {
                        "message": answer_msg_2,
                        "value": deviance_value
                    }
                ]

        def eval2():
            self.assertEqual(len(appl._midi.messages_sent), 0)
            self.assertEqual(display.label_note.text, note_text)

            if deviance_value != None:
                act_pos = display.deviance._marker.x / ((444 - deviance_width) / 2) - 1
                self.assertAlmostEqual(act_pos, max(-1, min(deviance_pos * deviance_zoom, 1)), delta = deviance_tolerance)

                self.assertEqual(display.label_note.text_color, exp_color)
                self.assertEqual(display.deviance._marker.fill, exp_color)
                self.assertEqual(display.deviance._marker.width, deviance_width)

            display.reset()

            if deviance_value != None:
                self.assertEqual(display.label_note.text_color, Colors.WHITE)

            return False
                
        
        # Build scenes hierarchy
        appl.next_step = SceneStep(
            num_pass_ticks = 5,
            prepare = prep1,
            evaluate = eval1,

            next = SceneStep(
                num_pass_ticks = 5,
                prepare = prep2,
                evaluate = eval2
            )
        )

        # Run process
        appl.process()
