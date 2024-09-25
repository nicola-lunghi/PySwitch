
from ...definitions import ConditionModes

# Condition to be filled with action specifications.
# Compares the value of the mapping to the passed one, and enables the action or action_not.
class Condition:
    def __init__(self, mapping, value, mode = ConditionModes.MODE_GREATER_EQUAL, action = None, action_not = None):
        pass