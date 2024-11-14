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
    "adafruit_midi.program_change": MockAdafruitMIDIProgramChange(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "adafruit_midi.start": MockAdafruitMIDIStart(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "gc": MockGC()
}):
    #from lib.pyswitch.controller.Controller import Controller
    from .mocks_appl import *
    from .mocks_ui import *
    from adafruit_midi.system_exclusive import SystemExclusive

    from lib.pyswitch.controller.actions.actions import ParameterAction
    from lib.pyswitch.controller.Client import ClientParameterMapping
    from lib.pyswitch.misc import compare_midi_messages, DEFAULT_LABEL_COLOR



class TestActionParameter(unittest.TestCase):
 
    def test_set_parameter(self):
        switch_1 = MockSwitch()
        
        mapping_1 = ClientParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x01, 0x02, 0x03, 0x04]
            )
        )

        action_1 = ParameterAction({
            "mode": PushButtonAction.MOMENTARY,
            "mapping": mapping_1,
            "valueEnable": 10,
            "valueDisable": 3,
            "color": (200, 100, 0),
            "ledBrightness": {
                "on": 0.5,
                "off": 0.1
            }
        })
        
        vp = MockValueProvider()
        led_driver = MockNeoPixelDriver()

        appl = MockController(
            led_driver = led_driver,
            communication = {
                "valueProvider": vp
            },
            midi = MockMidiController(),
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
            ]
        )

        # Build scene:
        # Step 1: Enable
        def prep1():
            switch_1.shall_be_pushed = True

        def eval1():
            self.assertEqual(len(vp.set_value_calls), 1)
            self.assertDictEqual(vp.set_value_calls[0], {
                "mapping": mapping_1,
                "value": 10
            })

            self.assertEqual(len(appl._midi.messages_sent), 1)
            self.assertTrue(compare_midi_messages(appl._midi.messages_sent[0], mapping_1.set))

            self.assertEqual(appl.switches[0].color, (200, 100, 0))
            self.assertEqual(appl.switches[0].brightness, 0.5)
            self.assertEqual(led_driver.leds[0], (100, 50, 0))
            
            return True        
        
        # Step 2: Disable
        def prep2():
            switch_1.shall_be_pushed = False

        def eval2():
            self.assertEqual(len(vp.set_value_calls), 2)
            self.assertDictEqual(vp.set_value_calls[1], {
                "mapping": mapping_1,
                "value": 3
            })

            self.assertEqual(len(appl._midi.messages_sent), 2)
            self.assertTrue(compare_midi_messages(appl._midi.messages_sent[1], mapping_1.set))

            self.assertEqual(appl.switches[0].color, (200, 100, 0))
            self.assertEqual(appl.switches[0].brightness, 0.1)
            self.assertEqual(led_driver.leds[0], (20, 10, 0))
                        
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


###############################################################################################


    def test_set_parameter_value_disable_auto(self):
        switch_1 = MockSwitch()
        period = MockPeriodCounter()
        
        mapping_1 = ClientParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x01, 0x02, 0x03, 0x04]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x21],
                data = [0x01, 0x02, 0x03, 0x05]
            )
        )

        action_1 = ParameterAction({
            "mode": PushButtonAction.MOMENTARY,
            "mapping": mapping_1,
            "valueEnable": 11,
            "valueDisable": "auto",
            "comparisonMode": ParameterAction.GREATER_EQUAL
        })
        
        vp = MockValueProvider()
        led_driver = MockNeoPixelDriver()

        appl = MockController(
            led_driver = led_driver,
            communication = {
                "valueProvider": vp
            },
            midi = MockMidiController(),
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

        answer_msg_1 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0x09, 0x44]
        )

        answer_msg_2 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0x07, 0x45]
        )

        # Build scene:
        # Check if nothing crashes if set is called before a value came in
        def prep1():
            switch_1.shall_be_pushed = True

        def eval1():
            self.assertEqual(len(vp.set_value_calls), 1)
            self.assertDictEqual(vp.set_value_calls[0], {
                "mapping": mapping_1,
                "value": 11
            })

            self.assertEqual(len(appl._midi.messages_sent), 1)
            self.assertTrue(compare_midi_messages(appl._midi.messages_sent[0], mapping_1.set))
            
            self.assertEqual(action_1.state, True)

            return True

        
        def prep2():
            switch_1.shall_be_pushed = False
            self.assertEqual(action_1._value_disable, "auto")

        def eval2():
            # Nothing must have been sent because we still have no disabling value
            self.assertEqual(len(vp.set_value_calls), 1)
            self.assertEqual(len(appl._midi.messages_sent), 1)
            
            self.assertEqual(action_1.state, False)

            return True
        
        # Receive a value
        def prep3():
            period.exceed_next_time = True
            appl._midi.next_receive_messages = [
                answer_msg_1,
                answer_msg_2
            ]
            vp.outputs_parse = [
                {
                    "mapping": mapping_1,
                    "result": True,
                    "value": 6
                },
                {
                    "result": False
                }
            ]

            return True

        def eval3():            
            self.assertEqual(action_1.state, False)
            self.assertEqual(action_1._value_disable, 6)

            return True     
        
        # Enable
        def prep4():
            switch_1.shall_be_pushed = True

        def eval4():
            self.assertEqual(len(vp.set_value_calls), 2)
            self.assertDictEqual(vp.set_value_calls[1], {
                "mapping": mapping_1,
                "value": 11
            })

            self.assertEqual(len(appl._midi.messages_sent), 2)
            self.assertTrue(compare_midi_messages(appl._midi.messages_sent[1], mapping_1.set))
            
            self.assertEqual(action_1.state, True)

            return True        
        
        # Receive a value when state is True (must not override the remembered value)
        def prep5():
            period.exceed_next_time = True
            appl._midi.next_receive_messages = [
                answer_msg_1
            ]
            vp.outputs_parse = [
                {
                    "mapping": mapping_1,
                    "result": True,
                    "value": 100
                }
            ]
            
            return True

        def eval5():            
            self.assertEqual(action_1.state, True)
            self.assertEqual(action_1._value_disable, 6)

            return True  
                
        # Disable again
        def prep6():
            switch_1.shall_be_pushed = False

        def eval6():
            self.assertEqual(len(vp.set_value_calls), 3)
            self.assertDictEqual(vp.set_value_calls[2], {
                "mapping": mapping_1,
                "value": 6
            })

            self.assertEqual(len(appl._midi.messages_sent), 3)
            self.assertTrue(compare_midi_messages(appl._midi.messages_sent[2], mapping_1.set))
                        
            self.assertEqual(action_1.state, False)

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
                        evaluate = eval4,

                        next = SceneStep(
                            num_pass_ticks = 5,
                            prepare = prep5,
                            evaluate = eval5,

                            next = SceneStep(
                                num_pass_ticks = 5,
                                prepare = prep6,
                                evaluate = eval6
                            )
                        )
                    )
                )
            )
        )

        # Run process
        appl.process()


###############################################################################################


    def test_set_parameter_values_disable_auto(self):
        switch_1 = MockSwitch()
        period = MockPeriodCounter()
        
        mapping_1 = ClientParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x01, 0x02, 0x03, 0x04]
            ),
            #response = SystemExclusive(
            #    manufacturer_id = [0x00, 0x10, 0x21],
            #    data = [0x01, 0x02, 0x03, 0x05]
            #)
        )

        mapping_2 = ClientParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x23],
                data = [0x01, 0x02, 0x03, 0x04]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x11, 0x21],
                data = [0x01, 0x02, 0x03, 0x05]
            )
        )

        action_1 = ParameterAction({
            "mode": PushButtonAction.MOMENTARY,
            "mapping": [
                mapping_1,            
                mapping_2
            ],
            "valueEnable": [11, 12],
            "valueDisable": [4, "auto"],
            "comparisonMode": ParameterAction.GREATER_EQUAL
        })
        
        vp = MockValueProvider()
        led_driver = MockNeoPixelDriver()

        appl = MockController(
            led_driver = led_driver,
            communication = {
                "valueProvider": vp
            },
            midi = MockMidiController(),
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

        answer_msg_1 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0x09, 0x44]
        )

        # Build scene:
        # Check if nothing crashes if set is called before a value came in
        def prep1():
            switch_1.shall_be_pushed = True

            self.assertEqual(action_1._update_value_disabled, [False, True])

        def eval1():
            self.assertEqual(len(vp.set_value_calls), 2)
            self.assertDictEqual(vp.set_value_calls[0], {
                "mapping": mapping_1,
                "value": 11
            })
            self.assertDictEqual(vp.set_value_calls[1], {
                "mapping": mapping_2,
                "value": 12
            })

            self.assertEqual(len(appl._midi.messages_sent), 2)
            self.assertTrue(compare_midi_messages(appl._midi.messages_sent[0], mapping_1.set))
            self.assertTrue(compare_midi_messages(appl._midi.messages_sent[1], mapping_2.set))
            
            self.assertEqual(action_1.state, True)

            return True

        
        def prep2():
            switch_1.shall_be_pushed = False
            self.assertEqual(action_1._value_disable, [4, "auto"])

        def eval2():
            # Only the non-auto mapping must have been sent
            self.assertEqual(len(vp.set_value_calls), 3)
            self.assertDictEqual(vp.set_value_calls[2], {
                "mapping": mapping_1,
                "value": 4
            })

            self.assertEqual(len(appl._midi.messages_sent), 3)
            self.assertTrue(compare_midi_messages(appl._midi.messages_sent[2], mapping_1.set))
            
            self.assertEqual(action_1.state, False)

            return True
        
        # Receive a value
        def prep3():
            period.exceed_next_time = True
            appl._midi.next_receive_messages = [
                answer_msg_1
            ]
            vp.outputs_parse = [
                {
                    "mapping": mapping_2,
                    "result": True,
                    "value": 7
                }
            ]
            
            return True

        def eval3():            
            self.assertEqual(action_1.state, False)
            self.assertEqual(action_1._value_disable, [4, 7])

            return True     
        
        # Enable
        def prep4():
            switch_1.shall_be_pushed = True

        def eval4():
            self.assertEqual(len(vp.set_value_calls), 5)
            self.assertDictEqual(vp.set_value_calls[3], {
                "mapping": mapping_1,
                "value": 11
            })
            self.assertDictEqual(vp.set_value_calls[4], {
                "mapping": mapping_2,
                "value": 12
            })

            self.assertEqual(len(appl._midi.messages_sent), 5)
            self.assertTrue(compare_midi_messages(appl._midi.messages_sent[3], mapping_1.set))
            self.assertTrue(compare_midi_messages(appl._midi.messages_sent[4], mapping_2.set))
            
            self.assertEqual(action_1.state, True)

            return True        
        
        # Receive a value when state is True (must not override the remembered value)
        def prep5():
            period.exceed_next_time = True
            appl._midi.next_receive_messages = [
                answer_msg_1
            ]
            vp.outputs_parse = [
                {
                    "mapping": mapping_2,
                    "result": True,
                    "value": 100
                }
            ]
            
            return True

        def eval5():            
            self.assertEqual(action_1.state, True)
            self.assertEqual(action_1._value_disable, [4, 7])

            return True     
        
        # Disable again
        def prep6():
            switch_1.shall_be_pushed = False

        def eval6():
            self.assertEqual(len(vp.set_value_calls), 7)
            self.assertDictEqual(vp.set_value_calls[5], {
                "mapping": mapping_1,
                "value": 4
            })
            self.assertDictEqual(vp.set_value_calls[6], {
                "mapping": mapping_2,
                "value": 7
            })

            self.assertEqual(len(appl._midi.messages_sent), 7)
            self.assertTrue(compare_midi_messages(appl._midi.messages_sent[5], mapping_1.set))
            self.assertTrue(compare_midi_messages(appl._midi.messages_sent[6], mapping_2.set))
                        
            self.assertEqual(action_1.state, False)

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
                        evaluate = eval4,

                        next = SceneStep(
                            num_pass_ticks = 5,
                            prepare = prep5,
                            evaluate = eval5,

                        next = SceneStep(
                            num_pass_ticks = 5,
                            prepare = prep6,
                            evaluate = eval6
                        )
                        )
                    )
                )
            )
        )

        # Run process
        appl.process()


###############################################################################################
 
 
    def test_set_parameter_disable_mapping(self):
        switch_1 = MockSwitch()
        
        mapping_1 = ClientParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x01, 0x02, 0x03, 0x04]
            )
        )

        mapping_disable_1 = ClientParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x01, 0x02, 0x33, 0x04]
            )
        )

        action_1 = ParameterAction({
            "mode": PushButtonAction.MOMENTARY,
            "mapping": mapping_1,
            "mappingDisable": mapping_disable_1,
            "valueEnable": 10,
            "valueDisable": 3,
            "color": (200, 100, 0),
            "ledBrightness": {
                "on": 0.5,
                "off": 0.1
            }
        })
        
        vp = MockValueProvider()
        led_driver = MockNeoPixelDriver()

        appl = MockController(
            led_driver = led_driver,
            communication = {
                "valueProvider": vp
            },
            midi = MockMidiController(),
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
            ]
        )

        # Build scene:
        # Step 1: Enable
        def prep1():
            switch_1.shall_be_pushed = True

        def eval1():
            self.assertEqual(len(vp.set_value_calls), 1)
            self.assertDictEqual(vp.set_value_calls[0], {
                "mapping": mapping_1,
                "value": 10
            })

            self.assertEqual(len(appl._midi.messages_sent), 1)
            self.assertTrue(compare_midi_messages(appl._midi.messages_sent[0], mapping_1.set))

            self.assertEqual(appl.switches[0].color, (200, 100, 0))
            self.assertEqual(appl.switches[0].brightness, 0.5)
            self.assertEqual(led_driver.leds[0], (100, 50, 0))
            
            return True        
        
        # Step 2: Disable
        def prep2():
            switch_1.shall_be_pushed = False

        def eval2():
            self.assertEqual(len(vp.set_value_calls), 2)
            self.assertDictEqual(vp.set_value_calls[1], {
                "mapping": mapping_disable_1,
                "value": 3
            })

            self.assertEqual(len(appl._midi.messages_sent), 2)
            self.assertTrue(compare_midi_messages(appl._midi.messages_sent[1], mapping_disable_1.set))

            self.assertEqual(appl.switches[0].color, (200, 100, 0))
            self.assertEqual(appl.switches[0].brightness, 0.1)
            self.assertEqual(led_driver.leds[0], (20, 10, 0))
                        
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


###############################################################################################


    def test_set_parameter_mappings_lists(self):
        switch_1 = MockSwitch()
        
        mapping_1 = ClientParameterMapping()

        mapping_2 = ClientParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x01, 0x02, 0x03, 0x04]
            )
        )

        mapping_3 = ClientParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x01, 0x02, 0x08, 0x04]
            )
        )

        mapping_disable_1 = ClientParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x01, 0x02, 0x33, 0x04]
            )
        )

        mapping_disable_2 = ClientParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x01, 0x02, 0x39, 0x04]
            )
        )

        action_1 = ParameterAction({
            "mode": PushButtonAction.MOMENTARY,
            "mapping": [
                mapping_1,
                mapping_2,
                mapping_3
            ],
            "mappingDisable": [
                mapping_disable_1,
                mapping_disable_2
            ],
            "valueEnable": [1, 2, 3],
            "valueDisable": [0, -1]
        })
        
        vp = MockValueProvider()
        led_driver = MockNeoPixelDriver()

        appl = MockController(
            led_driver = led_driver,
            communication = {
                "valueProvider": vp
            },
            midi = MockMidiController(),
            switches = [
                {
                    "assignment": {
                        "model": switch_1
                    },
                    "actions": [
                        action_1                        
                    ]
                }
            ]
        )

        # Build scene:
        # Step 1: Enable
        def prep1():
            switch_1.shall_be_pushed = True

        def eval1():
            self.assertEqual(len(vp.set_value_calls), 2)
            self.assertDictEqual(vp.set_value_calls[0], {
                "mapping": mapping_2,
                "value": 2
            })
            self.assertDictEqual(vp.set_value_calls[1], {
                "mapping": mapping_3,
                "value": 3
            })

            self.assertEqual(len(appl._midi.messages_sent), 2)
            self.assertTrue(compare_midi_messages(appl._midi.messages_sent[0], mapping_2.set))
            self.assertTrue(compare_midi_messages(appl._midi.messages_sent[1], mapping_3.set))

            return True        
        
        # Step 2: Disable
        def prep2():
            switch_1.shall_be_pushed = False

        def eval2():
            self.assertEqual(len(vp.set_value_calls), 4)
            self.assertDictEqual(vp.set_value_calls[2], {
                "mapping": mapping_disable_1,
                "value": 0
            })
            self.assertDictEqual(vp.set_value_calls[3], {
                "mapping": mapping_disable_2,
                "value": -1
            })

            self.assertEqual(len(appl._midi.messages_sent), 4)
            self.assertTrue(compare_midi_messages(appl._midi.messages_sent[2], mapping_disable_1.set))
            self.assertTrue(compare_midi_messages(appl._midi.messages_sent[3], mapping_disable_2.set))

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


###############################################################################################


    def test_set_parameter_with_label(self):
        switch_1 = MockSwitch()
        
        mapping_1 = ClientParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x01, 0x02, 0x03, 0x04]
            )
        )

        action_1 = ParameterAction({
            "mode": PushButtonAction.MOMENTARY,
            "mapping": mapping_1,
            "valueEnable": 10,
            "valueDisable": 3,
            "color": (200, 100, 0),
            "ledBrightness": {
                "on": 0.5,
                "off": 0.1
            },
            "displayDimFactor": {
                "on": 0.5,
                "off": 0.2
            },

            "text": "foo",
            "textDisabled": "bar"
        })
        
        vp = MockValueProvider()
        led_driver = MockNeoPixelDriver()

        appl = MockController(
            led_driver = led_driver,
            communication = {
                "valueProvider": vp
            },
            midi = MockMidiController(),
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
            ]
        )

        action_1.label = MockDisplayLabel()

        # Build scene:
        # Step 1: Enable
        def prep1():
            switch_1.shall_be_pushed = True

        def eval1():
            self.assertEqual(len(vp.set_value_calls), 1)
            self.assertDictEqual(vp.set_value_calls[0], {
                "mapping": mapping_1,
                "value": 10
            })

            self.assertEqual(len(appl._midi.messages_sent), 1)
            self.assertTrue(compare_midi_messages(appl._midi.messages_sent[0], mapping_1.set))

            self.assertEqual(appl.switches[0].color, (200, 100, 0))
            self.assertEqual(appl.switches[0].brightness, 0.5)
            self.assertEqual(led_driver.leds[0], (100, 50, 0))

            self.assertEqual(action_1.label.text, "foo")
            self.assertEqual(action_1.label.back_color, (100, 50, 0))
            
            return True        
        
        # Step 2: Disable
        def prep2():
            switch_1.shall_be_pushed = False

        def eval2():
            self.assertEqual(len(vp.set_value_calls), 2)
            self.assertDictEqual(vp.set_value_calls[1], {
                "mapping": mapping_1,
                "value": 3
            })

            self.assertEqual(len(appl._midi.messages_sent), 2)
            self.assertTrue(compare_midi_messages(appl._midi.messages_sent[1], mapping_1.set))

            self.assertEqual(appl.switches[0].color, (200, 100, 0))
            self.assertEqual(appl.switches[0].brightness, 0.1)
            self.assertEqual(led_driver.leds[0], (20, 10, 0))

            self.assertEqual(action_1.label.text, "bar")
            self.assertEqual(action_1.label.back_color, (40, 20, 0))
                        
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


###############################################################################################


    def test_set_parameter_with_label_no_text(self):
        switch_1 = MockSwitch()
        
        mapping_1 = ClientParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x01, 0x02, 0x03, 0x04]
            )
        )

        action_1 = ParameterAction({
            "mode": PushButtonAction.MOMENTARY,
            "mapping": mapping_1,
            "valueEnable": 10,
            "valueDisable": 3,
            "color": ((200, 100, 0), (10, 20, 30)),
            "ledBrightness": {
                "on": 0.5,
                "off": 0.1
            }
        })
        
        vp = MockValueProvider()
        led_driver = MockNeoPixelDriver()

        appl = MockController(
            led_driver = led_driver,
            communication = {
                "valueProvider": vp
            },
            midi = MockMidiController(),
            switches = [
                {
                    "assignment": {
                        "model": switch_1,
                        "pixels": (0, 1)
                    },
                    "actions": [
                        action_1                        
                    ]
                }
            ]
        )

        action_1.label = MockDisplayLabel()

        # Build scene:
        # Step 1: Enable
        def prep1():
            switch_1.shall_be_pushed = True

        def eval1():
            self.assertEqual(len(vp.set_value_calls), 1)
            self.assertDictEqual(vp.set_value_calls[0], {
                "mapping": mapping_1,
                "value": 10
            })

            self.assertEqual(len(appl._midi.messages_sent), 1)
            self.assertTrue(compare_midi_messages(appl._midi.messages_sent[0], mapping_1.set))

            self.assertEqual(appl.switches[0].colors, [(200, 100, 0), (10, 20, 30)])
            self.assertEqual(appl.switches[0].brightnesses, [0.5, 0.5])
            self.assertEqual(led_driver.leds[0], (100, 50, 0))
            self.assertEqual(led_driver.leds[1], (5, 10, 15))

            self.assertEqual(action_1.label.text, "")
            self.assertEqual(action_1.label.back_color, [(200, 100, 0), (10, 20, 30)])
            
            return True        
        
        # Step 2: Disable
        def prep2():
            switch_1.shall_be_pushed = False

        def eval2():
            self.assertEqual(len(vp.set_value_calls), 2)
            self.assertDictEqual(vp.set_value_calls[1], {
                "mapping": mapping_1,
                "value": 3
            })

            self.assertEqual(len(appl._midi.messages_sent), 2)
            self.assertTrue(compare_midi_messages(appl._midi.messages_sent[1], mapping_1.set))

            self.assertEqual(appl.switches[0].colors, [(200, 100, 0), (10, 20, 30)])
            self.assertEqual(appl.switches[0].brightnesses, [0.1, 0.1])
            self.assertEqual(led_driver.leds[0], (20, 10, 0))
            self.assertEqual(led_driver.leds[1], (1, 2, 3))

            self.assertEqual(action_1.label.text, "")
            self.assertEqual(action_1.label.back_color, [(40, 20, 0), (2, 4, 6)])
                        
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


###############################################################################################


    def test_request(self):
        self._test_request(ParameterAction.GREATER, 1, 0, 0, 0, False)
        self._test_request(ParameterAction.GREATER, 1, 0, 1, 0, False)
        self._test_request(ParameterAction.GREATER, 1, 0, 2, 0)
        self._test_request(ParameterAction.GREATER, 1, 0, 16383, 0)

        self._test_request(ParameterAction.GREATER_EQUAL, 1, 0, 0, 0, False)
        self._test_request(ParameterAction.GREATER_EQUAL, 1, 0, 1, 0)
        self._test_request(ParameterAction.GREATER_EQUAL, 1, 0, 2, 0)
        self._test_request(ParameterAction.GREATER_EQUAL, 1, 0, 16383, 0)

        self._test_request(ParameterAction.EQUAL, 1, 0, 0, 0, False)
        self._test_request(ParameterAction.EQUAL, 1, 0, 1, 0)
        self._test_request(ParameterAction.EQUAL, 1, 0, 2, 0, False)

        self._test_request(ParameterAction.LESS_EQUAL, 1, 2, 0, 2)
        self._test_request(ParameterAction.LESS_EQUAL, 1, 2, 1, 2)
        self._test_request(ParameterAction.LESS_EQUAL, 1, 2, 2, 2, False)
        self._test_request(ParameterAction.LESS_EQUAL, 1, 2, 3, 2, False)

        self._test_request(ParameterAction.LESS, 1, 2, 0, 2)
        self._test_request(ParameterAction.LESS, 1, 2, 1, 2, False)
        self._test_request(ParameterAction.LESS, 1, 2, 2, 2, False)
        self._test_request(ParameterAction.LESS, 1, 2, 3, 2, False)

        with self.assertRaises(Exception):
            self._test_request("invalid", 0, 1, 0, 1)


    def _test_request(self, mode, value_on, value_off, test_value_on, test_value_off, exp_state_on = True, exp_state_off = False):
        switch_1 = MockSwitch()
        
        mapping_1 = ClientParameterMapping(
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0x09]
            )
        )

        action_1 = ParameterAction({
            "mapping": mapping_1,
            "comparisonMode": mode,
            "valueEnable": value_on + 4,
            "valueDisable": value_off,
            "referenceValue": value_on
        })
        
        period = MockPeriodCounter()

        vp = MockValueProvider()

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            communication = {
                "valueProvider": vp
            },
            midi = MockMidiController(),
            switches = [
                {
                    "assignment": {
                        "model": switch_1
                    },
                    "actions": [
                        action_1                        
                    ]
                }
            ],
            period_counter = period
        )

        answer_msg_1 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0x09, 0x44]
        )

        answer_msg_2 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0x07, 0x45]
        )

        # Build scene:
        # Send update request
        def prep1():
            period.exceed_next_time = True

        def eval1():
            self.assertEqual(len(appl._midi.messages_sent), 1)
            self.assertEqual(appl._midi.messages_sent[0], mapping_1.request)
            return True

        # Step without update
        def eval2():
            self.assertEqual(len(appl._midi.messages_sent), 1)
            return True

        # Receive value 
        def prep3():
            period.exceed_next_time = True
            appl._midi.next_receive_messages = [
                answer_msg_1,
                answer_msg_2
            ]
            vp.outputs_parse = [
                {
                    "mapping": mapping_1,
                    "result": True,
                    "value": test_value_on
                },
                {
                    "result": False
                }
            ]

        def eval3():
            self.assertEqual(len(vp.parse_calls), 1)

            self.assertEqual(vp.parse_calls[0]["mapping"], mapping_1)
            self.assertTrue(compare_midi_messages(vp.parse_calls[0]["message"], answer_msg_1))

            self.assertEqual(mapping_1.value, test_value_on)
            self.assertEqual(action_1.state, exp_state_on)

            return True
        
        # Receive value 
        def prep4():
            period.exceed_next_time = True
            appl._midi.next_receive_messages = [
                answer_msg_1
            ]
            vp.outputs_parse = [
                {
                    "mapping": mapping_1,
                    "result": True,
                    "value": test_value_off
                }
            ]

        def eval4():
            self.assertEqual(len(vp.parse_calls), 2)

            self.assertEqual(vp.parse_calls[1]["mapping"], mapping_1)
            self.assertTrue(compare_midi_messages(vp.parse_calls[1]["message"], answer_msg_1))

            self.assertEqual(mapping_1.value, test_value_off)

            self.assertEqual(action_1.state, exp_state_off)

            return False

        # Build scenes hierarchy
        appl.next_step = SceneStep(
            num_pass_ticks = 5,
            prepare = prep1,
            evaluate = eval1,

            next = SceneStep(
                num_pass_ticks = 5,
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


###############################################################################################


    #def test_request_reference_value(self):
    #    switch_1 = MockSwitch()
        
    #    mapping_1 = ClientParameterMapping(
    #        set = SystemExclusive(
    #            manufacturer_id = [0x00, 0x10, 0x20],
    #            data = [0x01, 0x02, 0x03, 0x04]
    #        )
    #    )

    #    action_1 = ParameterAction({
    #        "mode": PushButtonAction.MOMENTARY,
    #        "mapping": mapping_1,
    #        "valueEnable": 11,
    #        "valueDisable": 3,
    #        "referenceValue": 10,
    #        "color": (200, 100, 0),
    #        "ledBrightness": {
    #            "on": 0.5,
    #            "off": 0.1
    #        }
    #    })
        
    #    vp = MockValueProvider()
    #    led_driver = MockNeoPixelDriver()

    #    appl = MockController(
    #        led_driver = led_driver,
    #        communication = {
    #            "valueProvider": vp
    #        },
    #        midi = MockMidiController(),
    #        switches = [
    #             {
    #                "assignment": {
    #                    "model": switch_1,
    #                    "pixels": [0]
    #                },
    #                "actions": [
    #                    action_1                        
    #                ]
    #            }
    #        ]
    #    )

    #    # Build scene:
    #    # Step 1: Enable
    #    def prep1():
    #        switch_1.shall_be_pushed = True

    #    def eval1():
    #        self.assertEqual(len(vp.set_value_calls), 1)
    #        self.assertDictEqual(vp.set_value_calls[0], {
    #            "mapping": mapping_1,
    #            "value": 11
    #        })

    #        self.assertEqual(len(appl._midi.messages_sent), 1)
    #        self.assertTrue(compare_midi_messages(appl._midi.messages_sent[0], mapping_1.set))

    #        self.assertEqual(appl.switches[0].color, (200, 100, 0))
    #        self.assertEqual(appl.switches[0].brightness, 0.5)
    #        self.assertEqual(led_driver.leds[0], (100, 50, 0))
            
    #        return True        
        
    #    # Step 2: Disable
    #    def prep2():
    #        switch_1.shall_be_pushed = False

    #    def eval2():
    #        self.assertEqual(len(vp.set_value_calls), 2)
    #        self.assertDictEqual(vp.set_value_calls[1], {
    #            "mapping": mapping_1,
    #            "value": 3
    #        })

    #        self.assertEqual(len(appl._midi.messages_sent), 2)
    #        self.assertTrue(compare_midi_messages(appl._midi.messages_sent[1], mapping_1.set))

    #        self.assertEqual(appl.switches[0].color, (200, 100, 0))
    #        self.assertEqual(appl.switches[0].brightness, 0.1)
    #        self.assertEqual(led_driver.leds[0], (20, 10, 0))
                        
    #        return False        

    #    # Build scenes hierarchy
    #    appl.next_step = SceneStep(
    #        num_pass_ticks = 5,
    #        prepare = prep1,
    #        evaluate = eval1,

    #        next = SceneStep(
    #            num_pass_ticks = 5,
    #            prepare = prep2,
    #            evaluate = eval2
    #        )
    #    )

    #    # Run process
    #    appl.process()
        

###############################################################################################


    def test_request_mappings_lists(self):
        switch_1 = MockSwitch()
        
        mapping_1 = ClientParameterMapping()

        mapping_2 = ClientParameterMapping(
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x27, 0x09]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x30, 0x19]
            )
        )

        mapping_3 = ClientParameterMapping(
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x27, 0x01]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x30, 0x29]
            )
        )

        action_1 = ParameterAction({
            "mapping": [
                mapping_1,
                mapping_2,
                mapping_3
            ],
            "valueEnable": [1, 2, 3],
            "valueDisable": [0, -1, -2]
        })
        
        period = MockPeriodCounter()
        vp = MockValueProvider()

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            communication = {
                "valueProvider": vp
            },
            midi = MockMidiController(),
            switches = [
                {
                    "assignment": {
                        "model": switch_1
                    },
                    "actions": [
                        action_1                        
                    ]
                }
            ],
            period_counter = period
        )

        answer_msg_1 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0x09, 0x44]
        )

        answer_msg_2 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0x07, 0x45]
        )

        # Build scene:
        # Send update request
        def prep1():
            period.exceed_next_time = True

        def eval1():
            self.assertEqual(len(appl._midi.messages_sent), 1)
            self.assertEqual(appl._midi.messages_sent[0], mapping_2.request)
            return True

        # Step without update
        def eval2():
            self.assertEqual(len(appl._midi.messages_sent), 1)
            return True

        # Receive value 
        def prep3():
            period.exceed_next_time = True
            appl._midi.next_receive_messages = [
                answer_msg_1,
                answer_msg_2
            ]
            vp.outputs_parse = [
                {
                    "mapping": mapping_2,
                    "result": True,
                    "value": 2
                },
                {
                    "result": False
                }
            ]

        def eval3():
            self.assertEqual(len(vp.parse_calls), 1)

            self.assertEqual(vp.parse_calls[0]["mapping"], mapping_2)
            self.assertTrue(compare_midi_messages(vp.parse_calls[0]["message"], answer_msg_1))

            self.assertEqual(mapping_2.value, 2)

            return True
        
        # Receive value 
        def prep4():
            period.exceed_next_time = True
            appl._midi.next_receive_messages = [
                answer_msg_1
            ]
            vp.outputs_parse = [
                {
                    "mapping": mapping_2,
                    "result": True,
                    "value": -1
                }
            ]

        def eval4():
            self.assertEqual(len(vp.parse_calls), 2)

            self.assertEqual(vp.parse_calls[1]["mapping"], mapping_2)
            self.assertTrue(compare_midi_messages(vp.parse_calls[1]["message"], answer_msg_1))

            self.assertEqual(mapping_2.value, -1)

            return False

        # Build scenes hierarchy
        appl.next_step = SceneStep(
            num_pass_ticks = 5,
            prepare = prep1,
            evaluate = eval1,

            next = SceneStep(
                num_pass_ticks = 5,
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


###############################################################################################


    def test_request_callback(self):
        switch_1 = MockSwitch()
        
        mapping_1 = ClientParameterMapping(
            set = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x01, 0x02, 0x03, 0x04]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x01, 0x02, 0x07, 0x09]
            )
        )

        cb_calls = []
        cb_data = {
            "return": False,
            "label_color": (0, 0, 0),
            "label_text": "",
            "pixel_color": (0, 0, 0),
            "pixel_brighness": 0,
            "calls": [],
            "exp_value": 0
        }

        that = self

        def cb(action, mapping):
            cb_data["calls"].append((action, mapping))

            if mapping.value != None:
                that.assertEqual(mapping.value, cb_data["exp_value"])

            if cb_data["return"]:
                action.label.text = cb_data["label_text"]
                action.label.back_color = cb_data["label_color"]

                action_1.switch_color = cb_data["pixel_color"]
                action_1.switch_brightness = cb_data["pixel_brightness"]

            return cb_data["return"]

        action_1 = ParameterAction({
            "mode": PushButtonAction.MOMENTARY,
            "mapping": mapping_1,
            "updateDisplays": cb,
            "color": (200, 200, 200),
            "text": "foo",
            "ledBrightness": {
                "on": 1,
                "off": 0.5
            },
            "displayDimFactor": {
                "on": 1,
                "off": 0.5
            }
        })

        vp = MockValueProvider()
        led_driver = MockNeoPixelDriver()
        period = MockPeriodCounter()

        appl = MockController(
            led_driver = led_driver,
            communication = {
                "valueProvider": vp
            },
            midi = MockMidiController(),
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

        action_1.label = MockDisplayLabel()
        
        answer_msg_1 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0x09, 0x44]
        )

        answer_msg_2 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0x07, 0x45]
        )

        # Build scene:
        # Check cb is not called on set
        def prep1():
            switch_1.shall_be_pushed = True

        def eval1():
            cb_data["calls"] = []
            return True        
        
        # Receive value: Default behaviour
        def prep2():
            switch_1.shall_be_pushed = False

            period.exceed_next_time = True
            appl._midi.next_receive_messages = [
                answer_msg_1,
                answer_msg_2
            ]
            vp.outputs_parse = [
                {
                    "mapping": mapping_1,
                    "result": True,
                    "value": 1
                },
                {
                    "result": False
                }
            ]

            cb_data["return"] = False
            cb_data["exp_value"] = 1

        def eval2():
            self.assertIn((action_1, mapping_1), cb_data["calls"])
            self.assertEqual(mapping_1.value, 1)

            self.assertEqual(action_1.label.back_color, (200, 200, 200))
            self.assertEqual(action_1.label.text, "foo")

            self.assertEqual(action_1.switch.color, (200, 200, 200))
            self.assertEqual(action_1.switch.brightness, 1)

            return True
        
        # Receive value: Callback does all things
        def prep3():
            period.exceed_next_time = True
            appl._midi.next_receive_messages = [
                answer_msg_1,
                answer_msg_2
            ]
            vp.outputs_parse = [
                {
                    "mapping": mapping_1,
                    "result": True,
                    "value": 22
                },
                {
                    "result": False
                }
            ]

            cb_data["return"] = True
            cb_data["label_color"] = (244, 233, 211)
            cb_data["label_text"] = "bar"
            cb_data["pixel_color"] = (22, 33, 44)
            cb_data["pixel_brightness"] = 0.4
            cb_data["exp_value"] = 22

        def eval3():
            self.assertEqual(mapping_1.value, 22)

            self.assertEqual(action_1.label.back_color, (244, 233, 211))
            self.assertEqual(action_1.label.text, "bar")

            self.assertEqual(action_1.switch.color, (22, 33, 44))
            self.assertEqual(action_1.switch.brightness, 0.4)

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
        
        
###############################################################################################


    def test_request_timeout(self):
        switch_1 = MockSwitch()
        
        mapping_1 = ClientParameterMapping(
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0x09]
            )
        )

        action_1 = ParameterAction({
            "mapping": mapping_1
        })
        
        period = MockPeriodCounter()

        vp = MockValueProvider()

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            communication = {
                "valueProvider": vp
            },
            midi = MockMidiController(),
            switches = [
                {
                    "assignment": {
                        "model": switch_1
                    },
                    "actions": [
                        action_1                        
                    ]
                }
            ],
            period_counter = period
        )

        appl.client._cleanup_terminated_period = MockPeriodCounter()
        wa = []

        # Build scene:
        # Send update request
        def prep1():
            period.exceed_next_time = True

        def eval1():
            self.assertEqual(len(appl._midi.messages_sent), 1)
            self.assertEqual(appl._midi.messages_sent[0], mapping_1.request)

            return True

        def prep2():
            period.exceed_next_time = True
            appl.client._cleanup_terminated_period.exceed_next_time = True

            appl.client._requests[0].lifetime = MockPeriodCounter()
            appl.client._requests[0].lifetime.exceed_next_time = True
            wa.append(appl.client._requests[0])

        # Step without update
        def eval2():
            self.assertEqual(len(appl.client._requests), 0)
            self.assertEqual(wa[0].finished, True)
            
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
        

###############################################################################################


    def test_force_update(self):
        switch_1 = MockSwitch()
        
        mapping_1 = ClientParameterMapping()

        action_1 = ParameterAction({
            "mapping": mapping_1,
            "color": (200, 100, 0)
        })
        
        period = MockPeriodCounter()
        vp = MockValueProvider()

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            communication = {
                "valueProvider": vp
            },
            midi = MockMidiController(),
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

        action_1.label = MockDisplayLabel()

        period.exceed_next_time = True
        switch_1.shall_be_pushed = True

        appl.next_step = SceneStep(
            num_pass_ticks = 5
        )

        # Run process
        appl.process()

        self.assertEqual(action_1.label.back_color, (200, 100, 0))
        self.assertEqual(appl.switches[0].color, (200, 100, 0))

        # Update displays after force_update
        action_1.label.back_color = (2, 2, 2)
        appl.switches[0].color = (2, 2, 2)

        action_1.force_update()

        action_1.update_displays()
            
        self.assertEqual(action_1.label.back_color, (200, 100, 0))
        self.assertEqual(appl.switches[0].color, (200, 100, 0))

        # Do not update when disabled
        action_1.enabled = False

        action_1.label.back_color = (2, 2, 2)
        appl.switches[0].color = (2, 2, 2)

        action_1.force_update()

        action_1.update_displays()
            
        self.assertEqual(action_1.label.back_color, (2, 2, 2))
        self.assertEqual(appl.switches[0].color, (2, 2, 2))


###############################################################################################


    def test_reset_displays(self):
        switch_1 = MockSwitch()        
        mapping_1 = ClientParameterMapping()

        action_1 = ParameterAction({
            "mapping": mapping_1,
            "color": (200, 100, 0)
        })
        
        period = MockPeriodCounter()
        vp = MockValueProvider()

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            communication = {
                "valueProvider": vp
            },
            midi = MockMidiController(),
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

        action_1.label = MockDisplayLabel()

        period.exceed_next_time = True
        switch_1.shall_be_pushed = True

        appl.next_step = SceneStep(
            num_pass_ticks = 5
        )

        # Run process
        appl.process()

        self.assertEqual(action_1.label.back_color, (200, 100, 0))
        self.assertEqual(appl.switches[0].color, (200, 100, 0))

        # Reset displays
        action_1.reset_display()
            
        self.assertEqual(action_1.label.back_color, DEFAULT_LABEL_COLOR)
        self.assertEqual(appl.switches[0].color, (0, 0, 0))
        self.assertEqual(appl.switches[0].brightness, 0)

        # Reset displays without label
        action_1.label = None
        appl.switches[0].color = (8, 8, 9)
        appl.switches[0].brightness = 0.3

        action_1.reset_display()
            
        self.assertEqual(appl.switches[0].color, (0, 0, 0))
        self.assertEqual(appl.switches[0].brightness, 0)


###############################################################################################


    def test_action_disabled(self):
        switch_1 = MockSwitch()
        
        mapping_1 = ClientParameterMapping(
            request = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x05, 0x07, 0x09]
            ),
            response = SystemExclusive(
                manufacturer_id = [0x00, 0x10, 0x20],
                data = [0x00, 0x00, 0x09]
            )
        )

        action_1 = ParameterAction({
            "mapping": mapping_1
        })
        
        period = MockPeriodCounter()

        vp = MockValueProvider()

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            communication = {
                "valueProvider": vp
            },
            midi = MockMidiController(),
            switches = [
                {
                    "assignment": {
                        "model": switch_1
                    },
                    "actions": [
                        action_1                        
                    ]
                }
            ],
            period_counter = period
        )

        answer_msg_1 = SystemExclusive(
            manufacturer_id = [0x00, 0x10, 0x20],
            data = [0x00, 0x00, 0x09, 0x44]
        )

        # Build scene:
        # Send update request
        def prep1():
            period.exceed_next_time = True

        def eval1():
            self.assertEqual(len(appl._midi.messages_sent), 1)
            self.assertEqual(appl._midi.messages_sent[0], mapping_1.request)
            return True

        # Step without update
        def eval2():
            self.assertEqual(len(appl._midi.messages_sent), 1)
            return True

        # Receive value 
        def prep3():
            period.exceed_next_time = True
            appl._midi.next_receive_messages = [
                answer_msg_1
            ]
            vp.outputs_parse = [
                {
                    "mapping": mapping_1,
                    "result": True,
                    "value": 1
                }
            ]
            action_1.enabled = False

        def eval3():
            self.assertEqual(len(vp.parse_calls), 1)

            self.assertEqual(mapping_1.value, 1)
            
            self.assertEqual(action_1.state, True)

            return False
        

        # Build scenes hierarchy
        appl.next_step = SceneStep(
            num_pass_ticks = 5,
            prepare = prep1,
            evaluate = eval1,

            next = SceneStep(
                num_pass_ticks = 5,
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