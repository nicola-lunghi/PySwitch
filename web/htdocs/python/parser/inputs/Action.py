import json
from .Arguments import Arguments

class Action:
    def __init__(self, input, element_node):
        self.node = element_node
        self.name = element_node.value.func.value
        self.input = input

        self.client = self._determine_client()

    # Returns a json encoded list of arguments of the node, represented by dicts.
    def arguments(self):
        visitor = Arguments()
        self.node.value.visit(visitor)
        return json.dumps(visitor.result)

    # Removes the action from the tree.
    def remove(self):
        self.input.remove_action(self.node)

    # Determine the client
    def _determine_client(self):
        import_statement = self.input.parser.determine_import_statement(self)
        if not import_statement:
            # No import statement: Perhaps this is defined in inputs.py directly, so we have no client
            return "local"

        for client in self.input.parser.clients:
            if client in import_statement:
                 return client

        return "local"