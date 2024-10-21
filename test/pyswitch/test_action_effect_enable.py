import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

# Import subject under test
with patch.dict(sys.modules, {
    "usb_midi": MockUsbMidi(),
    "adafruit_midi": MockAdafruitMIDI(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "gc": MockGC()
}):
    #from lib.pyswitch.controller.Controller import Controller
    from .mocks_appl import *
    from adafruit_midi.system_exclusive import SystemExclusive

    from lib.pyswitch.controller.actions.actions import EffectEnableAction, PushButtonModes
    from lib.pyswitch.controller.Client import ClientParameterMapping
    from lib.pyswitch.misc import Tools


class MockCategoryProvider:
    def get_effect_category(self, value):
        return value * 10
    
    # Must return the effect color for a mapping value
    def get_effect_category_color(self, value):
        return (value, value + 2, value * 4)
    
    # Must return the effect name for a mapping value
    def get_effect_category_name(self, value):
        return repr(value)
    
    # Must return the value interpreted as "not assigned"
    def get_category_not_assigned(self):
        return 0


class MockSlotInfoProvider:
    def __init__(self):
        self.output = "noname"

    def get_name(self):
        return self.output


class TestActionEffectEnable(unittest.TestCase):

    def test_request_parameter(self):
        switch_1 = MockSwitch()

        mapping_1 = ClientParameterMapping(
            name = "", 
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x01, 0x02, 0x03, 0x04]
            ),
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0x09]
            )
        )

        mapping_type_1 = ClientParameterMapping(
            name = "", 
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x10]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0x10]
            )
        )

        cp = MockCategoryProvider()

        action_1 = EffectEnableAction({
            "mode": PushButtonModes.MOMENTARY,
            "mapping": mapping_1,
            "mappingType": mapping_type_1,
            "categories": cp,
            "slotInfo": MockSlotInfoProvider(),
            "color": (10, 50, 100)
        })
        
        period = MockPeriodCounter()

        vp = MockValueProvider()
        led_driver = MockNeoPixelDriver()

        appl = MockController(
            led_driver = led_driver,
            value_provider = vp,
            switches = [
                {
                    "assignment": {
                        "model": switch_1,
                        "pixels": [0]
                    },
                    "actions": [
                        action_1                        
                    ]
                }
            ],
            period_counter = period
        )

        answer_msg_param = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0x09, 0x44]
        )

        answer_msg_type = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0x07, 0x45]
        )

        # Build scene:
        # Send update request
        def prep1():
            period.exceed_next_time = True

        def eval1():
            self.assertEqual(len(appl._midi.messages_sent), 1)            
            self.assertEqual(appl._midi.messages_sent[0], mapping_type_1.request)
            
            return True

        # Receive type
        def prep2():
            appl._midi.next_receive_messages = [
                answer_msg_type
            ]
            vp.outputs_parse = [
                {
                    "mapping": mapping_type_1,
                    "result": True,
                    "value": 0
                }
            ]

        def eval2():
            self.assertEqual(len(appl._midi.next_receive_messages), 0)

            self.assertEqual(len(appl._midi.messages_sent), 2)

            self.assertEqual(len(vp.parse_calls), 1)

            self.assertEqual(vp.parse_calls[0]["mapping"], mapping_type_1)
            self.assertTrue(Tools.compare_midi_messages(vp.parse_calls[0]["message"], answer_msg_type))
            self.assertEqual(mapping_type_1.value, 0)
            self.assertEqual(action_1._effect_category, 0)

            self.assertEqual(appl.switches[0].color, (0, 0, 0))
            self.assertEqual(appl.switches[0].brightness, 0.02)
            self.assertEqual(led_driver.leds[0], (0, 0, 0))

            return True

        # Receive status
        def prep3():
            appl._midi.next_receive_messages = [
                answer_msg_param
            ]
            vp.outputs_parse = [
                {
                    "mapping": mapping_1,
                    "result": True,
                    "value": 1
                }
            ]

        def eval3():
            self.assertEqual(len(appl._midi.next_receive_messages), 0)

            self.assertEqual(len(appl._midi.messages_sent), 2)
            
            self.assertEqual(len(vp.parse_calls), 2)

            self.assertEqual(vp.parse_calls[1]["mapping"], mapping_1)
            self.assertTrue(Tools.compare_midi_messages(vp.parse_calls[1]["message"], answer_msg_param))
            self.assertEqual(mapping_1.value, 1)

            self.assertEqual(appl.switches[0].color, (0, 2, 0))
            self.assertEqual(appl.switches[0].brightness, 1)
            self.assertEqual(led_driver.leds[0], (0, 2, 0))

            return True
        
        # Receive other value 
        def prep4():
            period.exceed_next_time = True
            appl._midi.next_receive_messages = [
                answer_msg_type
            ]
            vp.outputs_parse = [
                {
                    "mapping": mapping_type_1,
                    "result": True,
                    "value": 1
                }
            ]

        def eval4():
            self.assertEqual(len(vp.parse_calls), 3)

            self.assertEqual(vp.parse_calls[2]["mapping"], mapping_type_1)
            self.assertTrue(Tools.compare_midi_messages(vp.parse_calls[2]["message"], answer_msg_type))
            self.assertEqual(mapping_type_1.value, 1)
            self.assertEqual(action_1._effect_category, 10)

            self.assertEqual(appl.switches[0].color, (1, 3, 4))
            self.assertEqual(appl.switches[0].brightness, 1)
            self.assertEqual(led_driver.leds[0], (1, 3, 4))

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
                    evaluate = eval3,

                    next = SceneStep(
                        num_pass_ticks = 5,
                        prepare = prep4,
                        evaluate = eval4
                    )
                )
            )
        )

        # Run process
        appl.process()