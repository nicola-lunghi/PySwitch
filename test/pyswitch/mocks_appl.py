from time import sleep

from lib.pyswitch.controller.actions.Action import Action
from lib.pyswitch.controller.actions.actions import PushButtonAction
from lib.pyswitch.controller.Controller import Controller
from lib.pyswitch.controller.ConditionTree import Condition
from lib.pyswitch.misc import Tools

from .mocks_lib import *


# Used to build szenarios
class SceneStep:
    def __init__(self, num_pass_ticks = 0, prepare = None, evaluate = None, next = None):
        self.num_pass_ticks = num_pass_ticks
        self.prepare = prepare
        self.evaluate = evaluate
        self.next = next

    # Prepare step
    #def prepare(self):
    #    pass

    # Evaluate results of step. Returns if the loop should continue.
    #def evaluate(self, tick_result):
    #    return False  # Quit processing loop
    

##################################################################################################################################


class MockController(Controller):
    def __init__(self, led_driver, value_provider, config= {}, switches = [], displays = [], ui = None, period_counter = None):
        super().__init__(led_driver, value_provider, config, switches, displays, ui, period_counter)

        self._next_step = None
        self._cnt = 0

    def tick(self):
        if not self._next_step:
            return super().tick()
        
        if self._cnt < self._next_step.num_pass_ticks:
            self._cnt += 1
            return super().tick()
        
        self._cnt = 0
        if callable(self._next_step.prepare):
            self._next_step.prepare()

        res = super().tick()
        if not res:
            raise Exception("tick() does not return True")
        
        if not callable(self._next_step.evaluate):
            return False
        
        ret = self._next_step.evaluate()

        self._next_step = self._next_step.next

        return ret        
    
    @property
    def next_step(self):
        return self._next_step
    
    @next_step.setter
    def next_step(self, step):
        if not isinstance(step, SceneStep):
            raise Exception("Invalid test step")
        
        self._next_step = step


##################################################################################################################################


class MockPeriodCounter():
    def __init__(self):
        self.exceed_next_time = False
        self.num_reset_calls = 0

    def reset(self):
        self.num_reset_calls += 1

    @property
    def exceeded(self):
        if self.exceed_next_time:
            self.exceed_next_time = False
            return True
        return False


##################################################################################################################################


class MockNeoPixelDriver:
    class Led:
        def __init__(self):
            self.color = None
            self.brightness = None

    def __init__(self):
        self.leds = None
        
    def init(self, num_leds):
        self.leds = [None for i in range(num_leds)]


##################################################################################################################################


class MockSwitch:
    def __init__(self):
        self.shall_be_pushed = False

    def init(self):
        pass

    @property
    def pushed(self):
        return self.shall_be_pushed


##################################################################################################################################


class MockValueProvider:
    def __init__(self):
        self.outputs_parse = []
        self.parse_calls = []

        self.set_value_calls = []

    def parse(self, mapping, midi_message):        
        for o in self.outputs_parse:
            if not "mapping" in o or o["mapping"] != mapping:
                continue

            if "value" in o:
                mapping.value = o["value"]

            ret = o["result"] if "result" in o else False

            self.parse_calls.append({
                "mapping": mapping,
                "message": midi_message,
                "return": ret
            })

            return ret
        
        return False
    
    def set_value(self, mapping, value):
        self.set_value_calls.append({
            "mapping": mapping,
            "value": value
        })


##################################################################################################################################


class MockPushButtonAction(PushButtonAction):
    def __init__(self, config = {}, period_counter = None):
        super().__init__(config, period_counter)

        self.num_set_calls = 0

    def set(self, state):
        self.num_set_calls += 1
    

##################################################################################################################################


class MockAction(Action):

    def __init__(self, config = {}, update_delay_millis = 0):
        super().__init__(config)

        self.num_update_calls_overall = 0
        self.num_update_calls_enabled = 0
        self.update_delay_millis = update_delay_millis

    def update(self):
        self.num_update_calls_overall += 1
        
        if self.enabled:
            self.num_update_calls_enabled += 1

        if self.update_delay_millis > 0:
            sleep(self.update_delay_millis / 1000)


##################################################################################################################################


class MockCondition(Condition):
    def __init__(self, yes = None, no = None):
        super().__init__(yes = yes, no = no)

        self.bool_value = True
        self.num_update_calls = 0

    def update(self):
        self.num_update_calls += 1

        if self.true == self.bool_value:
            return

        self.true = self.bool_value

        for listener in self.listeners:
            listener.condition_changed(self)   


##################################################################################################################################


class MockMeasurement:
    def __init__(self):
        self.output_value = 0
        self.output_message = ""
        self.num_update_calls = 0

    def get_message(self):
        return self.output_message
    
    def value(self):
        return self.output_value

    def update(self):
        self.num_update_calls += 1


##################################################################################################################################


class MockConditionReplacer:
    def replace(self, entry):
        return entry + " (replaced)"
    

