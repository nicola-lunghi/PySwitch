import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

# Import subject under test
with patch.dict(sys.modules, {
    "micropython": MockMicropython,
    "displayio": MockDisplayIO(),
    "adafruit_display_text": MockAdafruitDisplayText(),
    "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
    "usb_midi": MockUsbMidi(),
    "adafruit_midi": MockAdafruitMIDI(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "gc": MockGC()
}):
    from adafruit_midi.system_exclusive import SystemExclusive

    from lib.pyswitch.ui.elements import ParameterDisplayLabel
    from lib.pyswitch.controller.Client import ClientParameterMapping

    from lib.pyswitch.ui.ui import DisplayBounds
    from lib.pyswitch.ui.UiController import UiController
    from lib.pyswitch.misc import compare_midi_messages

    from .mocks_appl import *
    from .mocks_ui import *


class TestParameterLabel(unittest.TestCase):

    def test(self):
        period = MockPeriodCounter()

        mapping_1 = ClientParameterMapping(
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x01, 0x02, 0x03, 0x04]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0x09, 0x00]
            )
        )

        display = ParameterDisplayLabel(
            parameter = {
                "mapping": mapping_1,
                "textReset": "resetted"
            },
            layout = {
                "font": "foo"
            },
            bounds = DisplayBounds(20, 30, 200, 300)
        )

        ui = UiController(MockDisplayDriver(init = True), MockFontLoader(), display)
        vp = MockValueProvider()

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            communication = {
                "valueProvider": vp
            },
            midi = MockMidiController(),            
            period_counter = period,
            ui = ui
        )

        answer_msg_1 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0x09, 0x44]
        )

        # Build scene:
        # Step 1: Not exceeded
        def prep1():
            period.exceed_next_time = True
            
        def eval1():
            self.assertEqual(len(appl._midi.messages_sent), 1)
            self.assertTrue(compare_midi_messages(appl._midi.messages_sent[0], mapping_1.request))

            return True

        # Step 2: Exceeded the first time
        def prep2():
            period.exceed_next_time = True

            appl._midi.next_receive_messages = [
                answer_msg_1
            ]
            vp.outputs_parse = [
                {
                    "mapping": mapping_1,
                    "result": True,
                    "value": "Some text"
                }
            ]   

        def eval2():
            self.assertEqual(display.text, "Some text")

            return True
        
        def prep3():
            display.reset()
            self.assertEqual(display.text, "resetted")
            self.assertEqual(display._last_value, None)      

        def eval3():
            return False

        # Build scenes hierarchy
        appl.next_step = SceneStep(
            prepare = prep1,
            evaluate = eval1,

            next = SceneStep(
                prepare = prep2,
                evaluate = eval2,

                next = SceneStep(
                    prepare = prep3,
                    evaluate = eval3
                )
            )
        )

        # Run process
        appl.process()

        
###########################################################################################


    def test_with_dependency(self):
        period = MockPeriodCounter()

        mapping_1 = ClientParameterMapping(
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x01, 0x02, 0x03, 0x04]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0x09, 0x00]
            )
        )

        mapping_2 = ClientParameterMapping(
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x21],
                data = [0x01, 0x02, 0x03, 0x05]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x11, 0x20],
                data = [0x00, 0x00, 0x09, 0x01]
            )
        )

        display = ParameterDisplayLabel(
            parameter = {
                "mapping": mapping_1,
                "depends": mapping_2
            },
            layout = {
                "font": "foo"
            },
            bounds = DisplayBounds(20, 30, 200, 300)
        )

        ui = UiController(MockDisplayDriver(init = True), MockFontLoader(), display)
        vp = MockValueProvider()

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            communication = {
                "valueProvider": vp
            },
            midi = MockMidiController(),
            period_counter = period,
            ui = ui
        )

        answer_msg_1 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0x09, 0x44]
        )

        # Build scene:
        # Step 1: Not exceeded
        def prep1():
            period.exceed_next_time = True
            
        def eval1():
            self.assertEqual(len(appl._midi.messages_sent), 1)
            self.assertTrue(compare_midi_messages(appl._midi.messages_sent[0], mapping_2.request))

            return True

        # Step 2: Exceeded the first time
        def prep2():
            period.exceed_next_time = True

            appl._midi.next_receive_messages = [
                answer_msg_1
            ]
            vp.outputs_parse = [
                {
                    "mapping": mapping_2,
                    "result": True,
                    "value": 3
                }
            ]   

        def eval2():
            self.assertEqual(len(appl._midi.messages_sent), 2)
            self.assertTrue(compare_midi_messages(appl._midi.messages_sent[1], mapping_1.request))

            self.assertEqual(display.text, "")            

            return True
        
        # Step 3: Not exceeded
        def prep3():
            period.exceed_next_time = True

            appl._midi.next_receive_messages = [
                answer_msg_1
            ]
            vp.outputs_parse = [
                {
                    "mapping": mapping_1,
                    "result": True,
                    "value": "Sometext"
                }
            ]   

        def eval3():
            self.assertEqual(display.text, "Sometext")            
            return False
        
        
        # Build scenes hierarchy
        appl.next_step = SceneStep(
            num_pass_ticks = 5,
            prepare = prep1,
            evaluate = eval1,

            next = SceneStep(
                num_pass_ticks = 5,
                prepare = prep2,
                evaluate = eval2,
            
                next = SceneStep(
                    num_pass_ticks = 5,
                    prepare = prep3,
                    evaluate = eval3
                )
            )
        )

        # Run process
        appl.process()


##################################################################################


    def test_timeout(self):
        period = MockPeriodCounter()

        mapping_1 = ClientParameterMapping(
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x01, 0x02, 0x03, 0x04]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0x09, 0x00]
            )
        )

        display = ParameterDisplayLabel(
            parameter = {
                "mapping": mapping_1,
                "textOffline": "offline"
            },
            layout = {
                "font": "foo"
            },
            bounds = DisplayBounds(20, 30, 200, 300)
        )

        ui = UiController(MockDisplayDriver(init = True), MockFontLoader(), display)
        vp = MockValueProvider()

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            communication = {
                "valueProvider": vp
            },
            midi = MockMidiController(),
            period_counter = period,
            ui = ui
        )

        wa = []

        # Build scene:
        # Step 1: Not exceeded
        def prep1():
            period.exceed_next_time = True
            
        def eval1():
            self.assertEqual(len(appl._midi.messages_sent), 1)
            self.assertTrue(compare_midi_messages(appl._midi.messages_sent[0], mapping_1.request))

            return True

        # Step 2: Exceeded the first time
        def prep2():
            period.exceed_next_time = True

            appl.client._cleanup_terminated_period = MockPeriodCounter()
            appl.client._cleanup_terminated_period.exceed_next_time = True

            appl.client._requests[0].lifetime = MockPeriodCounter()
            appl.client._requests[0].lifetime.exceed_next_time = True
            wa.append(appl.client._requests[0])

        def eval2():
            self.assertEqual(len(appl.client._requests), 0)
            self.assertEqual(wa[0].finished, True)

            self.assertEqual(display.text, "offline")      
            self.assertEqual(display._last_value, None)      

            return False
        

        # Build scenes hierarchy
        appl.next_step = SceneStep(
            prepare = prep1,
            evaluate = eval1,

            next = SceneStep(
                prepare = prep2,
                evaluate = eval2
            )
        )

        # Run process
        appl.process()