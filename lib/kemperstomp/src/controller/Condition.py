
from ...definitions import ConditionModes
from ..client.ClientRequest import ClientRequestListener
from ..misc.EventEmitter import EventEmitter
from ..misc.Tools import Tools


# Holds two model instances
class ConditionModel:
    def __init__(self, yes, no):
        self.yes = yes
        self.no = no


############################################################################################################################


# Condition to be filled with action specifications.
# Compares the value of the mapping to the passed one, and enables the action or action_not.
class Condition(ClientRequestListener, EventEmitter):
    def __init__(self, mapping, ref_value, mode = ConditionModes.MODE_GREATER_EQUAL, yes = None, no = None):
        super().__init__(ConditionListener)

        self.yes = yes
        self.no = no
        
        self._mapping = mapping
        self._ref_value = ref_value
        self._mode = mode

        self.model = None
        self._app = None
        self._last_value = None

    # Used internally: Set the model instances for the two values.
    def set_instances(self, appl, inst_yes, inst_no):
        self._appl = appl
        self._debug = Tools.get_option(self._appl.config, "debugConditions")

        self.model = ConditionModel(
            yes = inst_yes,
            no = inst_no
        )

    # Used internally: Updates the condition on every update tick
    def update(self):
        if self._appl == None:
            raise Exception("Condition not initialized")

        if self._debug == True:
            self._print("Requesting value")

        self._appl.client.request(self._mapping, self)

    # Evaluate a received value and return True or False (heart of the condition)
    def _evaluate_value(self, value):
        if self._mode == ConditionModes.MODE_GREATER_EQUAL:
            if value >= self._ref_value:
                return True
            else:
                return False
            
        elif self._mode == ConditionModes.MODE_STRING_CONTAINS:
            return self._ref_value in value
        
        else:
            raise Exception("Invalid condition mode: " + repr(self._mode))

    # Called by the Client class when a parameter request has been answered.
    # The value received is already set on the mapping.
    def parameter_changed(self, mapping):
        if mapping != self._mapping:
            return

        bool_value = self._evaluate_value(mapping.value)
            
        if self._last_value == bool_value:
            return

        self._last_value = bool_value

        if self._debug == True:
            self._print(" -> Received value " + repr(mapping.value) + ", evaluated to " + repr(bool_value))

        for listener in self.listeners:
            listener.condition_changed(self, bool_value)        

    # Called when the client is offline (requests took too long)
    def request_terminated(self, mapping):
        self._last_value = None

    # Debug console output
    def _print(self, msg):
        if self._debug != True:
            return
        
        Tools.print("Condition for " + self._mapping.name + ": " + msg)
        
        
############################################################################################################################


# Base class for evaluating condition changes
class ConditionListener:
    # Called on condition changes. The yes value will be True or False
    def condition_changed(self, condition, boolValue):
        pass

