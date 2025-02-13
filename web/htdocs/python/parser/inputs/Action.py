import json
from .Arguments import Arguments

class Action:
    def __init__(self, node):
        self.node = node
        self.name = node.func.value

    # Returns a json encoded list of arguments of the node, represented by dicts.
    def arguments(self):
        visitor = Arguments()
        self.node.visit(visitor)
        return json.dumps(visitor.result)
