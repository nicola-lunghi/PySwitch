import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

# Import subject under test
with patch.dict(sys.modules, {
    "micropython": MockMicropython,
    "usb_midi": MockUsbMidi(),
    "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
    "adafruit_midi": MockAdafruitMIDI(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "adafruit_midi.program_change": MockAdafruitMIDIProgramChange(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "gc": MockGC()
}):

    #from lib.pyswitch.controller.actions.actions import PushButtonAction
    from .mocks_appl import *
    from .mocks_callback import *


class TestActionPushButton(unittest.TestCase):

    def test_set_reset(self):
        cb = MockPushButtonActionCallback()

        action_1 = MockPushButtonAction({
            "mode": PushButtonAction.LATCH,
            "callback": cb
        })

        self.assertEqual(len(cb.update_displays_calls), 0)
        self.assertEqual(len(cb.state_changed_calls), 0)
        self.assertEqual(action_1.state, False)

        action_1.state = True
        self.assertEqual(len(cb.update_displays_calls), 1)
        self.assertEqual(len(cb.state_changed_calls), 1)
        self.assertEqual(action_1.state, True)

        action_1.feedback_state(False)
        self.assertEqual(len(cb.update_displays_calls), 1)
        self.assertEqual(len(cb.state_changed_calls), 1)
        self.assertEqual(action_1.state, False)

        action_1.feedback_state(True)
        self.assertEqual(len(cb.update_displays_calls), 1)
        self.assertEqual(len(cb.state_changed_calls), 1)
        self.assertEqual(action_1.state, True)

        action_1.state = False
        self.assertEqual(len(cb.update_displays_calls), 2)
        self.assertEqual(len(cb.state_changed_calls), 2)
        self.assertEqual(action_1.state, False)

        action_1.state = True
        self.assertEqual(len(cb.update_displays_calls), 3)
        self.assertEqual(len(cb.state_changed_calls), 3)
        self.assertEqual(action_1.state, True)

        action_1.reset()
        self.assertEqual(len(cb.update_displays_calls), 4)
        self.assertEqual(len(cb.state_changed_calls), 3)
        self.assertEqual(action_1.state, False)
        
        
###################################################################################


    def test_latch(self):
        switch_1 = MockSwitch()
        action_1 = MockPushButtonAction({
            "mode": PushButtonAction.LATCH
        })

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
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
        # Step 1: Button pushed
        def prep1():
            switch_1.shall_be_pushed = True
            self.assertEqual(action_1.state, False)

        def eval1():
            self.assertEqual(action_1.state, True)
            return True

        # Step 2: Button released
        def prep2():
            switch_1.shall_be_pushed = False
            self.assertEqual(action_1.state, True)

        def eval2():
            self.assertEqual(action_1.state, True)
            return True
        
        # Step 3: Button pushed
        def prep3():
            switch_1.shall_be_pushed = True
            self.assertEqual(action_1.state, True)

        def eval3():
            self.assertEqual(action_1.state, False)
            return True
        
        # Step 4: Button released
        def prep4():
            switch_1.shall_be_pushed = False
            self.assertEqual(action_1.state, False)

        def eval4():
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
                        evaluate = eval4
                    )
                )
            )
        )

        # Run process
        appl.process()

        
###################################################################################


    def test_enable(self):
        switch_1 = MockSwitch()
        action_1 = MockPushButtonAction({
            "mode": PushButtonAction.ENABLE
        })

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
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
        # Step 1: Button pushed
        def prep1():
            switch_1.shall_be_pushed = True
            self.assertEqual(action_1.state, False)

        def eval1():
            self.assertEqual(action_1.state, True)
            return True

        # Step 2: Button released
        def prep2():
            switch_1.shall_be_pushed = False
            self.assertEqual(action_1.state, True)

        def eval2():
            self.assertEqual(action_1.state, True)
            return True
        
        # Step 3: Button pushed
        def prep3():
            switch_1.shall_be_pushed = True
            self.assertEqual(action_1.state, True)

        def eval3():
            self.assertEqual(action_1.state, True)
            return True
        
        # Step 4: Button released
        def prep4():
            switch_1.shall_be_pushed = False
            self.assertEqual(action_1.state, True)

        def eval4():
            self.assertEqual(action_1.state, True)
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

        
###################################################################################


    def test_disable(self):
        switch_1 = MockSwitch()
        action_1 = MockPushButtonAction({
            "mode": PushButtonAction.DISABLE
        })
        action_1.state = True

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
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
        # Step 1: Button pushed
        def prep1():
            switch_1.shall_be_pushed = True
            self.assertEqual(action_1.state, True)

        def eval1():
            self.assertEqual(action_1.state, False)
            return True

        # Step 2: Button released
        def prep2():
            switch_1.shall_be_pushed = False
            self.assertEqual(action_1.state, False)

        def eval2():
            self.assertEqual(action_1.state, False)
            return True
        
        # Step 3: Button pushed
        def prep3():
            switch_1.shall_be_pushed = True
            self.assertEqual(action_1.state, False)

        def eval3():
            self.assertEqual(action_1.state, False)
            return True
        
        # Step 4: Button released
        def prep4():
            switch_1.shall_be_pushed = False
            self.assertEqual(action_1.state, False)

        def eval4():
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
                        evaluate = eval4
                    )
                )
            )
        )

        # Run process
        appl.process()

        
###################################################################################


    def test_momentary(self):
        switch_1 = MockSwitch()
        action_1 = MockPushButtonAction({
            "mode": PushButtonAction.MOMENTARY
        })

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
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
        # Step 1: Button pushed
        def prep1():
            switch_1.shall_be_pushed = True
            self.assertEqual(action_1.state, False)

        def eval1():
            self.assertEqual(action_1.state, True)
            return True

        # Step 2: Button released
        def prep2():
            switch_1.shall_be_pushed = False
            self.assertEqual(action_1.state, True)

        def eval2():
            self.assertEqual(action_1.state, False)
            return True
        
        # Step 3: Button pushed
        def prep3():
            switch_1.shall_be_pushed = True
            self.assertEqual(action_1.state, False)

        def eval3():
            self.assertEqual(action_1.state, True)
            return True
        
        # Step 4: Button released
        def prep4():
            switch_1.shall_be_pushed = False
            self.assertEqual(action_1.state, True)

        def eval4():
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
                        evaluate = eval4
                    )
                )
            )
        )

        # Run process
        appl.process()

        
###################################################################################


    # def test_momentary_inverse(self):
    #     switch_1 = MockSwitch()
    #     action_1 = MockPushButtonAction({
    #         "mode": PushButtonAction.MOMENTARY_INVERSE
    #     })
    #     action_1.state = True

    #     appl = MockController(
    #         led_driver = MockNeoPixelDriver(),
    #         midi = MockMidiController(),
    #         switches = [
    #             {
    #                 "assignment": {
    #                     "model": switch_1
    #                 },
    #                 "actions": [
    #                     action_1
    #                 ]
    #             }
    #         ]
    #     )

    #     # Build scene:
    #     # Step 1: Button pushed
    #     def prep1():
    #         switch_1.shall_be_pushed = True
    #         self.assertEqual(action_1.state, True)

    #     def eval1():
    #         self.assertEqual(action_1.state, False)
    #         return True

    #     # Step 2: Button released
    #     def prep2():
    #         switch_1.shall_be_pushed = False
    #         self.assertEqual(action_1.state, False)

    #     def eval2():
    #         self.assertEqual(action_1.state, True)
    #         return True
        
    #     # Step 3: Button pushed
    #     def prep3():
    #         switch_1.shall_be_pushed = True
    #         self.assertEqual(action_1.state, True)

    #     def eval3():
    #         self.assertEqual(action_1.state, False)
    #         return True
        
    #     # Step 4: Button released
    #     def prep4():
    #         switch_1.shall_be_pushed = False
    #         self.assertEqual(action_1.state, False)

    #     def eval4():
    #         self.assertEqual(action_1.state, True)
    #         return False

    #     # Build scenes hierarchy
    #     appl.next_step = SceneStep(
    #         num_pass_ticks = 5,
    #         prepare = prep1,
    #         evaluate = eval1,

    #         next = SceneStep(
    #             num_pass_ticks = 5,
    #             prepare = prep2,
    #             evaluate = eval2,
            
    #             next = SceneStep(
    #                 num_pass_ticks = 5,
    #                 prepare = prep3,
    #                 evaluate = eval3,
            
    #                 next = SceneStep(
    #                     num_pass_ticks = 5,
    #                     prepare = prep4,
    #                     evaluate = eval4
    #                 )
    #             )
    #         )
    #     )

    #     # Run process
    #     appl.process()

        
###################################################################################


    def test_one_shot(self):
        switch_1 = MockSwitch()
        cb = MockPushButtonActionCallback()
        action_1 = MockPushButtonAction({
            "mode": PushButtonAction.ONE_SHOT,
            "callback": cb
        })

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
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
        # Step 1: Button pushed
        def prep1():
            switch_1.shall_be_pushed = True
            cb.update_displays_calls = []
            cb.state_changed_calls = []

        def eval1():
            self.assertEqual(len(cb.update_displays_calls), 1)
            self.assertEqual(len(cb.state_changed_calls), 1)
            return True

        # Step 2: Button released
        def prep2():
            switch_1.shall_be_pushed = False
            self.assertEqual(len(cb.update_displays_calls), 1)
            self.assertEqual(len(cb.state_changed_calls), 1)

        def eval2():
            self.assertEqual(len(cb.update_displays_calls), 2)
            self.assertEqual(len(cb.state_changed_calls), 1)
            return True
        
        # Step 3: Button pushed
        def prep3():
            switch_1.shall_be_pushed = True
            self.assertEqual(len(cb.update_displays_calls), 2)
            self.assertEqual(len(cb.state_changed_calls), 1)

        def eval3():
            self.assertEqual(len(cb.update_displays_calls), 3)
            self.assertEqual(len(cb.state_changed_calls), 2)
            return True
        
        # Step 4: Button released
        def prep4():
            switch_1.shall_be_pushed = False
            self.assertEqual(len(cb.update_displays_calls), 3)
            self.assertEqual(len(cb.state_changed_calls), 2)

        def eval4():
            self.assertEqual(len(cb.update_displays_calls), 4)
            self.assertEqual(len(cb.state_changed_calls), 2)
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

        
###################################################################################


    def test_hold_momentary_short_press(self):
        switch_1 = MockSwitch()
        period = MockPeriodCounter()        
        action_1 = MockPushButtonAction(
            {
                "mode": PushButtonAction.HOLD_MOMENTARY,
                "holdTimeMillis": 500
            },
            period
        )

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
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
        # Step 1: Button pushed
        def prep1():
            switch_1.shall_be_pushed = True
            self.assertEqual(action_1.state, False)
            self.assertEqual(period.num_reset_calls, 0)

        def eval1():
            self.assertEqual(action_1.state, True)
            self.assertEqual(period.num_reset_calls, 1)
            return True

        # Step 2: Button released
        def prep2():
            switch_1.shall_be_pushed = False
            self.assertEqual(action_1.state, True)
            self.assertEqual(period.num_reset_calls, 1)

        def eval2():
            self.assertEqual(action_1.state, True)
            self.assertEqual(period.num_reset_calls, 1)
            return True
        
        # Step 3: Button pushed
        def prep3():
            switch_1.shall_be_pushed = True
            self.assertEqual(action_1.state, True)
            self.assertEqual(period.num_reset_calls, 1)

        def eval3():
            self.assertEqual(action_1.state, False)
            self.assertEqual(period.num_reset_calls, 2)
            return True
        
        # Step 4: Button released
        def prep4():
            switch_1.shall_be_pushed = False
            self.assertEqual(action_1.state, False)
            self.assertEqual(period.num_reset_calls, 2)

        def eval4():
            self.assertEqual(action_1.state, False)
            self.assertEqual(period.num_reset_calls, 2)
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


###################################################################################


    def test_hold_momentary_long_press(self):
        switch_1 = MockSwitch()
        period = MockPeriodCounter()
        action_1 = MockPushButtonAction(
            {
                "mode": PushButtonAction.HOLD_MOMENTARY,
                "holdTimeMillis": 500
            },
            period
        )

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
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
        # Step 1: Button pushed
        def prep1():
            switch_1.shall_be_pushed = True
            self.assertEqual(action_1.state, False)

        def eval1():
            self.assertEqual(action_1.state, True)
            return True

        # Step 2: Button released
        def prep2():
            period.exceed_next_time = True
            switch_1.shall_be_pushed = False
            self.assertEqual(action_1.state, True)

        def eval2():
            self.assertEqual(action_1.state, False)
            return True
        
        # Step 3: Button pushed
        def prep3():            
            switch_1.shall_be_pushed = True
            self.assertEqual(action_1.state, False)

        def eval3():
            self.assertEqual(action_1.state, True)
            return True
        
        # Step 4: Button released
        def prep4():
            switch_1.shall_be_pushed = False
            self.assertEqual(action_1.state, True)

        def eval4():
            self.assertEqual(action_1.state, True)
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