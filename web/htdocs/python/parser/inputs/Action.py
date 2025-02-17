import json
from .Arguments import Arguments

class Action:
    def __init__(self, input, element_node):
        self.node = element_node
        self.name = element_node.value.func.value
        self.input = input

    # Returns a json encoded list of arguments of the node, represented by dicts.
    def arguments(self):
        visitor = Arguments()
        self.node.value.visit(visitor)
        return json.dumps(visitor.result)

    # Removes the action from the tree.
    def remove(self):
        self.input.remove_action(self.node)