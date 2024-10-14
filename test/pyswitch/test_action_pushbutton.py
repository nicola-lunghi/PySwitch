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
    from lib.pyswitch.controller.actions.actions import PushButtonModes
    from .mocks_appl import *


class TestActionPushButton(unittest.TestCase):

    def test_latch(self):
        switch_1 = MockSwitch()
        action_1 = MockPushButtonAction({
            "mode": PushButtonModes.LATCH
        })

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            value_provider = MockValueProvider(),
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

        that = self

        # Build scene:
        # Step 1: Button pushed
        def prep1():
            switch_1.shall_be_pushed = True
            that.assertEqual(action_1.state, False)

        def eval1():
            that.assertEqual(action_1.state, True)
            return True

        # Step 2: Button released
        def prep2():
            switch_1.shall_be_pushed = False
            that.assertEqual(action_1.state, True)

        def eval2():
            that.assertEqual(action_1.state, True)
            return True
        
        # Step 3: Button pushed
        def prep3():
            switch_1.shall_be_pushed = True
            that.assertEqual(action_1.state, True)

        def eval3():
            that.assertEqual(action_1.state, False)
            return True
        
        # Step 4: Button released
        def prep4():
            switch_1.shall_be_pushed = False
            that.assertEqual(action_1.state, False)

        def eval4():
            that.assertEqual(action_1.state, False)
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
            "mode": PushButtonModes.ENABLE
        })

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            value_provider = MockValueProvider(),
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

        that = self

        # Build scene:
        # Step 1: Button pushed
        def prep1():
            switch_1.shall_be_pushed = True
            that.assertEqual(action_1.state, False)

        def eval1():
            that.assertEqual(action_1.state, True)
            return True

        # Step 2: Button released
        def prep2():
            switch_1.shall_be_pushed = False
            that.assertEqual(action_1.state, True)

        def eval2():
            that.assertEqual(action_1.state, True)
            return True
        
        # Step 3: Button pushed
        def prep3():
            switch_1.shall_be_pushed = True
            that.assertEqual(action_1.state, True)

        def eval3():
            that.assertEqual(action_1.state, True)
            return True
        
        # Step 4: Button released
        def prep4():
            switch_1.shall_be_pushed = False
            that.assertEqual(action_1.state, True)

        def eval4():
            that.assertEqual(action_1.state, True)
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
            "mode": PushButtonModes.DISABLE
        })
        action_1.state = True

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            value_provider = MockValueProvider(),
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

        that = self

        # Build scene:
        # Step 1: Button pushed
        def prep1():
            switch_1.shall_be_pushed = True
            that.assertEqual(action_1.state, True)

        def eval1():
            that.assertEqual(action_1.state, False)
            return True

        # Step 2: Button released
        def prep2():
            switch_1.shall_be_pushed = False
            that.assertEqual(action_1.state, False)

        def eval2():
            that.assertEqual(action_1.state, False)
            return True
        
        # Step 3: Button pushed
        def prep3():
            switch_1.shall_be_pushed = True
            that.assertEqual(action_1.state, False)

        def eval3():
            that.assertEqual(action_1.state, False)
            return True
        
        # Step 4: Button released
        def prep4():
            switch_1.shall_be_pushed = False
            that.assertEqual(action_1.state, False)

        def eval4():
            that.assertEqual(action_1.state, False)
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
            "mode": PushButtonModes.MOMENTARY
        })

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            value_provider = MockValueProvider(),
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

        that = self

        # Build scene:
        # Step 1: Button pushed
        def prep1():
            switch_1.shall_be_pushed = True
            that.assertEqual(action_1.state, False)

        def eval1():
            that.assertEqual(action_1.state, True)
            return True

        # Step 2: Button released
        def prep2():
            switch_1.shall_be_pushed = False
            that.assertEqual(action_1.state, True)

        def eval2():
            that.assertEqual(action_1.state, False)
            return True
        
        # Step 3: Button pushed
        def prep3():
            switch_1.shall_be_pushed = True
            that.assertEqual(action_1.state, False)

        def eval3():
            that.assertEqual(action_1.state, True)
            return True
        
        # Step 4: Button released
        def prep4():
            switch_1.shall_be_pushed = False
            that.assertEqual(action_1.state, True)

        def eval4():
            that.assertEqual(action_1.state, False)
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


    def test_momentary_inverse(self):
        switch_1 = MockSwitch()
        action_1 = MockPushButtonAction({
            "mode": PushButtonModes.MOMENTARY_INVERSE
        })
        action_1.state = True

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            value_provider = MockValueProvider(),
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

        that = self

        # Build scene:
        # Step 1: Button pushed
        def prep1():
            switch_1.shall_be_pushed = True
            that.assertEqual(action_1.state, True)

        def eval1():
            that.assertEqual(action_1.state, False)
            return True

        # Step 2: Button released
        def prep2():
            switch_1.shall_be_pushed = False
            that.assertEqual(action_1.state, False)

        def eval2():
            that.assertEqual(action_1.state, True)
            return True
        
        # Step 3: Button pushed
        def prep3():
            switch_1.shall_be_pushed = True
            that.assertEqual(action_1.state, True)

        def eval3():
            that.assertEqual(action_1.state, False)
            return True
        
        # Step 4: Button released
        def prep4():
            switch_1.shall_be_pushed = False
            that.assertEqual(action_1.state, False)

        def eval4():
            that.assertEqual(action_1.state, True)
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


    def test_one_shot(self):
        switch_1 = MockSwitch()
        action_1 = MockPushButtonAction({
            "mode": PushButtonModes.ONE_SHOT
        })

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            value_provider = MockValueProvider(),
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

        that = self

        # Build scene:
        # Step 1: Button pushed
        def prep1():
            switch_1.shall_be_pushed = True
            that.assertEqual(action_1.num_set_calls, 0)

        def eval1():
            that.assertEqual(action_1.num_set_calls, 1)
            return True

        # Step 2: Button released
        def prep2():
            switch_1.shall_be_pushed = False
            that.assertEqual(action_1.num_set_calls, 1)

        def eval2():
            that.assertEqual(action_1.num_set_calls, 1)
            return True
        
        # Step 3: Button pushed
        def prep3():
            switch_1.shall_be_pushed = True
            that.assertEqual(action_1.num_set_calls, 1)

        def eval3():
            that.assertEqual(action_1.num_set_calls, 2)
            return True
        
        # Step 4: Button released
        def prep4():
            switch_1.shall_be_pushed = False
            that.assertEqual(action_1.num_set_calls, 2)

        def eval4():
            that.assertEqual(action_1.num_set_calls, 2)
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


    def test_hold_momentary(self):
        switch_1 = MockSwitch()
        action_1 = MockPushButtonAction({
            "mode": PushButtonModes.HOLD_MOMENTARY
        })

        appl = MockController(
            led_driver = MockNeoPixelDriver(),
            value_provider = MockValueProvider(),
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

        that = self

        # Build scene:
        # Step 1: Button pushed
        def prep1():
            switch_1.shall_be_pushed = True
            that.assertEqual(action_1.num_set_calls, 0)

        def eval1():
            that.assertEqual(action_1.num_set_calls, 1)
            return True

        # Step 2: Button released
        def prep2():
            switch_1.shall_be_pushed = False
            that.assertEqual(action_1.num_set_calls, 1)

        def eval2():
            that.assertEqual(action_1.num_set_calls, 1)
            return True
        
        # Step 3: Button pushed
        def prep3():
            switch_1.shall_be_pushed = True
            that.assertEqual(action_1.num_set_calls, 1)

        def eval3():
            that.assertEqual(action_1.num_set_calls, 2)
            return True
        
        # Step 4: Button released
        def prep4():
            switch_1.shall_be_pushed = False
            that.assertEqual(action_1.num_set_calls, 2)

        def eval4():
            that.assertEqual(action_1.num_set_calls, 2)
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

        