import json
import libcst
import uuid
from .Arguments import Arguments

class Action:
    def __init__(self, input, call_node):
        self.__id = str(uuid.uuid4())

        self.node = call_node
        self.input = input 
        self.assign = None

        self._evaluate_node()
        self.client = self._determine_client()

        # Buffers
        self._arguments = None

    def _evaluate_node(self):
        # Is it a function call? Most actions are.
        if isinstance(self.node, libcst.Call):
            self.name = self.node.func.value
            self.node_content = self.node
            
        # No call: Search if there is an assignment with the name
        elif isinstance(self.node, libcst.Name):
            assign_node = self.input.parser.get_assignment(self.node.value)

            if assign_node:
                self.assign = self.node.value
                
                self.name = assign_node.func.value
                self.node_content = assign_node
            else:
                self.name = self.node.value
                self.node_content = self.node
                

    # Unique ID
    def id(self):
        return self.__id

    # Returns a json encoded list of arguments of the node, represented by dicts.
    def arguments(self):
        if self._arguments:
            return json.dumps(self._arguments)
        
        visitor = Arguments(self.name)        
        self.node_content.visit(visitor)
        self._arguments = visitor.result

        return json.dumps(self._arguments)

    # Returns the value of an argument as string, or None if not found
    def argument(self, name):
        if not self._arguments:
            self.arguments()

        for arg in self._arguments:
            if arg["name"] == name:
                return arg["value"]
            
        return None

    # Removes the action from the tree.
    def remove(self):
        self._arguments = None
        self.input.remove_action(self.node)

    # If the action is connected to a pager, this returns the page ID, or None if not.
    def page(self):
        if not self.pager():
            return None
        
        return self.argument("id")
    
    # Returns the pager name, if any
    def pager(self):
        ec = self.argument("enable_callback")
        if not ec:
            return None
        
        if not self.argument("id") or self.argument("id") == "None":
            return None
        
        splt = ec.split(".")
        if len(splt) != 2:
            return None
        
        return splt[0]

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