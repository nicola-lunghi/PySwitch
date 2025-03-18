import uuid
import libcst
import json

from .Arguments import Arguments

class ItemBase:
    def __init__(self, parser, call_node, file_id):
        self.__id = str(uuid.uuid4())
        self.__file_id = file_id

        self.parser = parser
        self.node = call_node
        self.assign = None

        # Buffers
        self._arguments = None

        self._evaluate_node()

    # Unique ID
    def id(self):
        return self.__id

    # Evaluate the node after it has been set
    def _evaluate_node(self):
        self.proxy_name = None

        # Is it a function call? Most actions are.
        if isinstance(self.node, libcst.Call):
            self.name = libcst.parse_module("").code_for_node(self.node.func)
            self.node_content = self.node

            if isinstance(self.node.func, libcst.Attribute):                
                # Determine the name of the action for a proxy function
                proxy_call = self.parser.get_assignment(self.node.func.value.value, self.__file_id)
                if proxy_call:
                    self.proxy_name = proxy_call.func.value + "." + self.node.func.attr.value

        # No call: Search if there is an assignment with the name
        elif isinstance(self.node, libcst.Name):
            assign_node = self.parser.get_assignment(self.node.value, self.__file_id)
            
            if assign_node:
                self.assign = self.node.value
                
                self.name = assign_node.func.value
                self.node_content = assign_node
            else:
                self.name = self.node.value
                self.node_content = self.node
                
    # Returns a json encoded list of arguments of the node, represented by dicts.
    def arguments(self):
        if self._arguments:
            return json.dumps(self._arguments)
        
        visitor = Arguments(self.name)        
        self.node_content.visit(visitor)
        self._arguments = visitor.result

        return json.dumps(self._arguments)

    # Returns the value of an argument as string, or None if not found 
    # (only applies to keyword arguments of course)
    def argument(self, name):
        if not self._arguments:
            self.arguments()

        for arg in self._arguments:
            if "name" in arg and arg["name"] == name:
                return arg["value"]
            
        return None

