from lib.pyswitch.controller.actions.Action import Action
from lib.pyswitch.controller.actions.actions import PushButtonAction
from lib.pyswitch.controller.Controller import Controller
from lib.pyswitch.controller.Client import ClientParameterMapping

from .mocks_lib import *


# Used to build szenarios
class SceneStep:
    def __init__(self, num_pass_ticks = 0, prepare = None, evaluate = None, next = None):
        self.num_pass_ticks = num_pass_ticks
        self.prepare = prepare
        self.evaluate = evaluate
        self.next = next


##################################################################################################################################


class MockController(Controller):
    def __init__(self, led_driver, midi, protocol = None, config = {}, switches = [],  ui = None, period_counter = None, no_tick = False):
        super().__init__(
            led_driver = led_driver, 
            protocol = protocol,
            midi = midi, 
            config = config, 
            switches = switches, 
            ui = ui, 
            period_counter = period_counter
        )

        self._next_step = None
        self._cnt = 0
        self._no_tick = no_tick

    def tick(self):
        if self._no_tick:
            return False
        
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


class MockMidiController:
    def __init__(self):
        self.messages_sent = []
        self.next_receive_messages = []

    def receive(self):
        if self.next_receive_messages:
            return self.next_receive_messages.pop(0)
        
        return None
    
    def send(self, midi_message):
        self.messages_sent.append(midi_message)


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
    def __init__(self):
        self.leds = None
        
    def init(self, num_leds):
        self.leds = [None for i in range(num_leds)]


##################################################################################################################################


class MockSwitch:
    def __init__(self, port = None):
        self.port = port
        self.shall_be_pushed = False
        self.raise_on_init = None

    def init(self):
        if self.raise_on_init:
            raise self.raise_on_init

    @property
    def pushed(self):
        return self.shall_be_pushed


##################################################################################################################################


class MockParameterMapping(ClientParameterMapping):
    def __init__(self, name = "", set = None, request = None, response = None, value = None):
        super().__init__(name = name, set = set, request = request, response = response, value = value)

        self.outputs_parse = []
        self.output_result_finished = None
        self.set_value_calls = []

    def parse(self, midi_message):
        for o in self.outputs_parse:
            if midi_message != o["message"]:
                continue

            if "value" in o:
                value = o["value"]

                if "valueIndex" in o:
                    value_index = o["valueIndex"]

                    if not isinstance(self.value, list):
                        self.value = []
                    
                    while len(self.value) < value_index + 1:
                        self.value.append(None)

                    self.value[value_index] = value
                else:
                    self.value = value
        
            return True
        return False
    
    def set_value(self, value):
        self.set_value_calls.append(value)

    def result_finished(self):
        if self.output_result_finished != None:
            return self.output_result_finished
        else:
            return super().result_finished()
    

##################################################################################################################################


class MockPushButtonAction(PushButtonAction):
    def __init__(self, config = {}, period_counter = None):
        super().__init__(config = config, period_counter = period_counter)

        self.num_set_calls = 0

    def set(self, state):
        self.num_set_calls += 1
    

##################################################################################################################################


class MockAction(Action):

    def __init__(self, config = {}):
        super().__init__(config = config)

        self.reset_mock()

    def reset_mock(self):
        self.num_update_calls_overall = 0
        self.num_update_calls_enabled = 0
        self.num_reset_calls = 0
        self.num_push_calls = 0
        self.num_release_calls = 0
        self.num_update_displays_calls = 0
        
        self.state = False

    def push(self):
        self.num_push_calls += 1

    def release(self):
        self.num_release_calls += 1

    def update(self):
        super().update()

        self.num_update_calls_overall += 1
        
        if self.enabled:
            self.num_update_calls_enabled += 1

    def reset(self):
        self.num_reset_calls += 1

    def update_displays(self):
        super().update_displays()

        self.num_update_displays_calls += 1


##################################################################################################################################


class MockClient:
    def __init__(self):
        self.register_calls = []
        self.request_calls = []
        self.set_calls = []
        self.num_notify_connection_lost_calls = 0

    def set(self, mapping, value):
        self.set_calls.append({
            "mapping": mapping,
            "value": value
        })

    def register(self, mapping, listener):
        self.register_calls.append({
            "mapping": mapping,
            "listener": listener
        })

    def request(self, mapping, listener):
        self.request_calls.append({
            "mapping": mapping,
            "listener": listener
        })

    def notify_connection_lost(self):
        self.num_notify_connection_lost_calls += 1

##################################################################################################################################


class MockClientRequestListener:
    def __init__(self):
        self.parameter_changed_calls = []
        self.request_terminated_calls = []

    def parameter_changed(self, mapping):
        self.parameter_changed_calls.append(mapping)

    # Called when the client is offline (requests took too long)
    def request_terminated(self, mapping):
        self.request_terminated_calls.append(mapping)


##################################################################################################################################


class MockBidirectionalProtocol:
    def __init__(self):
        self.outputs_is_bidirectional = []
        self.outputs_feedback_value = []
        self.output_color = (0, 0, 0)

        self.num_update_calls = 0

        self.init_calls = []
        self.receive_calls = []

    def init(self, midi, client):
        self.init_calls.append({
            "midi": midi,
            "client": client
        })

    # Must return (boolean) if the passed mapping is handled in the bidirectional protocol
    def is_bidirectional(self, mapping):
        for o in self.outputs_is_bidirectional:
            if o["mapping"] == mapping:
                return o["result"]
            
        return False
   
    # Must return (boolean) if the passed mapping should feed back the set value immediately
    # without waiting for a midi message.
    def feedback_value(self, mapping):
        for o in self.outputs_feedback_value:
            if o["mapping"] == mapping:
                return o["result"]
            
        return False

    # Initialize the communication etc.
    def update(self):
        self.num_update_calls += 1
   
    # Receive midi messages (for example for state sensing)
    def receive(self, midi_message):
        self.receive_calls.append(midi_message)

    # Must return a color representation for the current state
    def get_color(self):
        return self.output_color

