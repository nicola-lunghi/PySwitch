
from ...client.ClientRequest import ClientRequestListener
from ...misc.EventEmitter import EventEmitter
from ..Updateable import Updateable


# Holds two customer model data fields
class ConditionModel:
    def __init__(self, yes, no):
        self.yes = yes
        self.no = no


############################################################################################################################


# Return structure for Condition.parse()
class ConditionParseResult:
    def __init__(self, objects = [], conditions = []):
        self.objects = objects
        self.conditions = conditions


############################################################################################################################


# Condition to be filled with action specifications.
# Compares the value of the mapping to the passed one, and enables the action or action_not.
class Condition(ClientRequestListener, EventEmitter, Updateable):
    def __init__(self, yes = None, no = None):
        super().__init__(ConditionListener)

        self.yes = yes
        self.no = no
        
        self.model = None
        self.appl = None

    # Called when the UI is ready
    def init(self, appl):
        self.appl = appl

    # Parses the passed subject, eitehr a list of containing homogenous structure of lists, 
    # customer objects and conditions holding the same, or a single object. Returns the list of instances created by 
    # factory, if it did return something, along with a list of conditions to be updated periodically.
    @staticmethod    
    def parse(subject, listener = None, factory = None, enable = True, allow_lists = True):
        if subject == None:
            return ConditionParseResult()
        
        elif isinstance(subject, list):
            if allow_lists != True:
                raise Exception("No lists allowed for conditional parameter")
            
            ret = ConditionParseResult()
            for a in subject:
                res = Condition.parse(
                    a, 
                    enable = enable,
                    listener = listener,
                    factory = factory
                )

            ret.objects = ret.objects + res.objects
            ret.conditions = ret.conditions + res.conditions

            return ret

        elif isinstance(subject, Condition):
            # Condition based: Create actions for both outcomes
            result_yes = Condition.parse(
                subject.yes, 
                enable = enable,
                listener = listener,
                factory = factory
            )

            result_no = Condition.parse(
                subject.no,
                enable = False,
                listener = listener,
                factory = factory
            )
            
            # Set the actions on the condition for later access
            subject.model = ConditionModel(
                yes = result_yes.objects,
                no = result_no.objects
            )

            # Add this instance as listener on condition changes
            if listener != None:
                subject.add_listener(listener)

            return ConditionParseResult(
                objects = result_yes.objects + result_no.objects + [subject],
                conditions = result_yes.conditions + result_no.conditions + [subject]
            )
        
        else:
            # Simple action definition
            if factory != None:
                # Optional: Factory to create model objects. If not passed, 
                # the subjects themselves are collected in the condition models.
                object = factory.get_condition_instance(subject, enable)
                if object == None:
                    return ConditionParseResult()
            
                return ConditionParseResult(
                    objects = [object]
                )
            else:
                return ConditionParseResult(
                    objects = [subject]
                )

        
############################################################################################################################


# Base class for evaluating condition changes
class ConditionListener:
    # Called on condition changes. The yes value will be True or False
    def condition_changed(self, condition, bool_value):
        pass

        
############################################################################################################################


# Base class for evaluating customer data in Condition.parse()
class ConditionModelFactory:
    # data is the customer data in the condition configs, enabled signals if the
    # condition branch is active by default (assuming that all conditions are true by default).
    # Can return a model instance or something else which will be collected in the Condition models,
    # so the listeners can access them later (optional).
    def get_condition_instance(self, data, enabled):
        return None

