
from ...client.ClientRequest import ClientRequestListener
from ...misc.EventEmitter import EventEmitter
from ..Updateable import Updateable


# Holds two model instances
class ConditionModel:
    def __init__(self, yes, no):
        self.yes = yes
        self.no = no


############################################################################################################################


# Condition to be filled with action specifications.
# Compares the value of the mapping to the passed one, and enables the action or action_not.
class Condition(ClientRequestListener, EventEmitter, Updateable):
    def __init__(self, yes = None, no = None):
        super().__init__(ConditionListener)

        self.yes = yes
        self.no = no
        
        self.model = None

    # Used internally: Set the model instances for the two values.
    def set_instances(self, appl, inst_yes, inst_no):
        self.model = ConditionModel(
            yes = inst_yes,
            no = inst_no
        )

        
############################################################################################################################


# Base class for evaluating condition changes
class ConditionListener:
    # Called on condition changes. The yes value will be True or False
    def condition_changed(self, condition, bool_value):
        pass

