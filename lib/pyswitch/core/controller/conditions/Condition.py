
from ...client.ClientRequest import ClientRequestListener
from ...misc.EventEmitter import EventEmitter
from ..Updateable import Updateable


# Holds two customer model data fields
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
        self.appl = None

    # Set the model instances for the two values.
    def init(self, appl, model):
        self.appl = appl
        self.model = model

    # Parses the passed subject, eitehr a list of containing homogenous structure of lists, 
    # customer objects and conditions holding the same, or a single object. Returns the list of instances created by 
    # factory, if it did return something.
    @staticmethod    
    def parse(appl, subject, listener = None, factory = None, enable = True):
        if subject == None:
            return []
        
        elif isinstance(subject, list):
            objects = []
            for a in subject:
                objects = objects + Condition.parse(
                    appl,
                    a, 
                    enable = enable,
                    listener = listener,
                    factory = factory
                )
            return objects

        elif isinstance(subject, Condition):
            # Condition based: Create actions for both outcomes
            objects_yes = Condition.parse(
                appl,
                subject.yes, 
                enable = enable,
                listener = listener,
                factory = factory
            )

            objects_no = Condition.parse(
                appl,
                subject.no,
                enable = False,
                listener = listener,
                factory = factory
            )
            
            # Set the actions on the condition for later access
            subject.init(
                appl,
                ConditionModel(
                    yes = objects_yes,
                    no = objects_no
                )
            )

            # Add this instance as listener on condition changes
            if listener != None:
                subject.add_listener(listener)

            # Add the condition to the global list of conditions, so it will
            # be updated periodically
            appl.updateables.append(subject)

            return objects_yes + objects_no
        
        else:
            # Simple action definition
            if factory != None:
                # Optional: Factory to create model objects. If not passed, 
                # the subjects themselves are collected in the condition models.
                object = factory.get_condition_instance(subject, enable)
                if object == None:
                    return []
            
                return [object]
            else:
                return [subject]

        
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

