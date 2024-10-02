from ...client.ClientRequest import ClientRequestListener

from .Condition import Condition
from ...misc.Tools import Tools


# Comparison modes for ParameterCondition
class ParameterConditionModes:    
    # Numeric
    MODE_EQUAL = 0                   # Reference value must be a numeric value
    
    MODE_GREATER = 10                # Reference value must be a numeric value
    MODE_GREATER_EQUAL = 21          # Reference value must be a numeric value
    
    MODE_LESS = 20                   # Reference value must be a numeric value
    MODE_LESS_EQUAL = 21             # Reference value must be a numeric value
    
    MODE_IN_RANGE = 90               # Reference value must be a tuple with lower / higher borders (inclusive). For example: (0, 1.2)

    # Strings
    MODE_STRING_CONTAINS = 500       # Reference value must be a string
    MODE_STRING_NOT_CONTAINS = 501   # Reference value must be a string
    MODE_STRING_STARTS_WITH = 510    # Reference value must be a string
    MODE_STRING_ENDS_WITH = 520      # Reference value must be a string


########################################################################################################################################


# Condition to be filled with action specifications.
# Compares the value of the mapping to the passed one, and enables the action or action_not.
class ParameterCondition(Condition, ClientRequestListener):
    def __init__(self, mapping, ref_value, mode = ParameterConditionModes.MODE_GREATER_EQUAL, yes = None, no = None):
        super().__init__(yes = yes, no = no)

        self._mapping = mapping
        self._ref_value = ref_value
        self._mode = mode

        self._current_raw_value = None

    # Used internally: Set the model instances for the two values.
    def init(self, appl):
        super().init(appl)

        self._debug = Tools.get_option(self.appl.config, "debugConditions")

    # Used internally: Updates the condition on every update tick
    def update(self):
        if not self.appl:
            raise Exception("Condition not initialized")

        if self._debug:
            self._print("Requesting value")

        self.appl.client.request(self._mapping, self)

    # Evaluate a received value and return True or False (heart of the condition)
    def _evaluate_value(self, value):
        if self._mode == ParameterConditionModes.MODE_GREATER:
            return value > self._ref_value            
            
        elif self._mode == ParameterConditionModes.MODE_GREATER_EQUAL:
            return value >= self._ref_value            
            
        elif self._mode == ParameterConditionModes.MODE_LESS:
            return value < self._ref_value            
            
        elif self._mode == ParameterConditionModes.MODE_LESS_EQUAL:
            return value <= self._ref_value            
            
        elif self._mode == ParameterConditionModes.MODE_EQUAL:
            return value == self._ref_value            
            
        elif self._mode == ParameterConditionModes.MODE_IN_RANGE:
            return value >= self._ref_value[0] and value <= self._ref_value[1]
            
        elif self._mode == ParameterConditionModes.MODE_STRING_CONTAINS:
            return self._ref_value in value
        
        elif self._mode == ParameterConditionModes.MODE_STRING_NOT_CONTAINS:
            return self._ref_value not in value
        
        elif self._mode == ParameterConditionModes.MODE_STRING_STARTS_WITH:
            return value.startswith(self._ref_value)
        
        elif self._mode == ParameterConditionModes.MODE_STRING_ENDS_WITH:
            return value.endswith(self._ref_value)
        
        else:
            raise Exception("Invalid condition mode: " + repr(self._mode))

    # Called by the Client class when a parameter request has been answered.
    # The value received is already set on the mapping.
    def parameter_changed(self, mapping):
        if mapping != self._mapping:
            return
        
        if mapping.value == self._current_raw_value:
            return

        self._current_raw_value = mapping.value

        bool_value = self._evaluate_value(mapping.value)
            
        if self.true == bool_value:
            return

        self.true = bool_value

        if self._debug:
            self._print(" -> Received value " + repr(mapping.value) + ", evaluated to " + repr(self.true))

        for listener in self.listeners:
            listener.condition_changed(self)        

    # Called when the client is offline (requests took too long)
    def request_terminated(self, mapping):
        if mapping != self._mapping:
            return
        
        self.true = True

    # Debug console output
    def _print(self, msg):
        if not self._debug:
            return
        
        Tools.print("Condition for " + self._mapping.name + ": " + msg)
        
        