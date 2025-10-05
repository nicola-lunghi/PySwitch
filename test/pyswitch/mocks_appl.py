from uuid import uuid4
from functools import wraps

from pyswitch.controller.actions import Action, PushButtonAction
from pyswitch.controller.client import ClientParameterMapping
from pyswitch.misc import Updateable, Updater

from .mocks_lib import *


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
        
        self.passed = 0
        self.interval = 0

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
    class LedList(list):
        def fill(self, color):
            pass

    def __init__(self):
        self.leds = None
        
    def init(self, num_leds):
        self.leds = self.LedList()
        for i in range(num_leds):
            self.leds.append(None)        
        

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


class MockPotentiometer:
    def __init__(self):
        self.output = 0

    def init(self):
        pass

    @property
    def value(self):
        return self.output
    

##################################################################################################################################


class MockRotaryEncoder: 
    def __init__(self):
        self.num_init_calls = 0
        self.output = 0

    def init(self):
        self.num_init_calls += 1

    @property
    def position(self):
        return self.output

##################################################################################################################################

def _check_unique_mapping_names(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if len(args) > 0:
            name = args[0]
        else:
            name = kwargs["name"]

        for m in ClientParameterMapping._mappings:
            if m.name == name:
                raise Exception("Mapping already defined: " + repr(name))

        return function(*args, **kwargs)
    return wrapper

ClientParameterMapping.__init__ = _check_unique_mapping_names(ClientParameterMapping.__init__)

class MockParameterMapping(ClientParameterMapping):
    def __init__(self, name = None, set = None, request = None, response = None, value = None, type = 0, depends = None):
        super().__init__(
            name = name if name != None else uuid4(), 
            create_key = ClientParameterMapping, 
            set = set, 
            request = request, 
            response = response, 
            value = value, 
            type = type, 
            depends = depends
        )

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

        self.output_push = None
        self.output_release = None

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
        return self.output_push

    def release(self):
        self.num_release_calls += 1
        return self.output_release

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


class MockAnalogAction:
    def __init__(self, enabled = True):
        self.enabled = enabled
        self.init_calls = []
        self.process_calls = []
    
    def init(self, appl):
        self.init_calls.append(appl)

    # Process a value in range [0..65535]
    def process(self, value):
        self.process_calls.append(value)

    def reset(self):
        pass


##################################################################################################################################


class MockEncoderAction(Updateable):
    def __init__(self):
        self.enabled = True
        self.init_calls = []
        self.process_calls = []
        self.num_update_calls = 0

    def init(self, appl):
        self.init_calls.append(appl)

    def update(self):
        self.num_update_calls += 1

    def process(self, position):
        self.process_calls.append(position)

    def reset(self):
        pass

##################################################################################################################################


def MockInputControllerDefinition():
    return {
        "assignment": {
            "model": MockPotentiometer()
        },
        "actions": {
            MockAnalogAction(),
            MockAnalogAction()
        }
    }


##################################################################################################################################


class MockClient:
    def __init__(self):
        self.register_calls = []
        self.request_calls = []
        self.set_calls = []
        self.num_notify_connection_lost_calls = 0
        self.debug = False
        self.midi = MockMidiController()

    @property
    def last_sent_message(self):
        return self.set_calls[len(self.set_calls)-1] if self.set_calls else None

    def set(self, mapping, value):
        self.set_calls.append({
            "mapping": mapping,
            "value": value
        })

    def register(self, mapping, listener = None):
        self.register_calls.append({
            "mapping": mapping,
            "listener": listener
        })

    def request(self, mapping, listener = None):
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


##################################################################################################################################


class MockWriter:
    def __init__(self):
        self.contents = ""

    def write(self, data):
        self.contents += data


##################################################################################################################################


class MockFootswitch:
    def __init__(self, pixels = [0, 1, 2], actions = [], order = 0, id = 0):
        self.pixels = pixels
        self.actions = actions

        self.colors = [(0, 0, 0) for i in pixels]
        self.brightnesses = [0 for i in pixels]
        
        self.override_action = None
        self.strobe_order = order
        self.id = id

    @property
    def color(self):
        return self.colors[0]
    
    @color.setter
    def color(self, color):
        self.colors = [color for i in self.colors]


    @property
    def brightness(self):
        return self.brightnesses[0]
    
    @brightness.setter
    def brightness(self, brightness):
        self.brightnesses = [brightness for i in self.brightnesses]


##################################################################################################################################

class MockController(Updater):
    def __init__(self, config = {}, ui = None, inputs = [], num_leds = 0, client = None):
        Updater.__init__(self)

        self.client = MockClient() if not client else client
        self.config = config
        self.ui = ui
        self.inputs = inputs
        self.shared = {}

        self.led_driver = MockNeoPixelDriver()
        self.led_driver.init(num_leds)

    def reset_actions(self):
        pass
