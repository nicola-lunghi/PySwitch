
from ...misc.EventEmitter import EventEmitter
from ..Updateable import Updateable


# Base condition to be filled with custom objects or lists (which can be or contain Conditions themselves).
# Compares the value of the mapping to the passed one, and notifies listeners when the value has changed.
class Condition(EventEmitter, Updateable):
    def __init__(self, yes = None, no = None):
        super().__init__(ConditionListener)

        self.yes = yes    # Positive value
        self.no = no      # Negative value

        self.true = True  # Current state of the condition
        
        self.appl = None

    # Called when the UI is ready (some child classes need an appl reference, this is not used here)
    def init(self, appl):
        self.appl = appl

        
############################################################################################################################


# Base class for evaluating condition changes
class ConditionListener:
    # Called on condition changes. The changed condition is passed, however you may more
    # likely use the ConditionTree value(s) instead.
    def condition_changed(self, condition):
        pass

        
