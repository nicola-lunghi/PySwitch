
from .Condition import Condition


# Condition to be filled with action specifications.
# Listens to another action (which must be a PushButtonAction).
class PushButtonCondition(Condition):
    def __init__(self, id, enabled = None, disabled = None):
        super().__init__(yes = enabled, no = disabled)
        
        self._id = id

    # Used internally: Set the model instances for the two values.
    def init(self, appl):
        super().init(appl)
        
        self._action = self._determine_action(self._id)

    # Used internally: Updates the condition on every update tick
    def update(self):
        bool_value = self._action.state

        if self.true == bool_value:
            return

        self.true = bool_value

        for listener in self.listeners:
            listener.condition_changed(self)   

    # Determine the action by ID
    def _determine_action(self, id):
        if self.appl == None:
            raise Exception("Condition not initialized")
        
        for switch in self.appl.switches:
            for action in switch.actions:
                if action.id == id:
                    return action
                
        raise Exception("Action with ID " + repr(id) + " not defined")
