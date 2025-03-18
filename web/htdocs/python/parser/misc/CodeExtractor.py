import libcst
from .AssignmentExtractor import AssignmentExtractor

class CodeExtractor:

    def __init__(self, cst):
        self.cst = cst

    # Can be redefined to define unnamed parameter names for specific types
    # which will be added automatically.
    def get_arg_names(self, type_name):
        return []

    # Can be redefined to add/manipulate data for Call output nodes
    def postprocess_call(self, call_data):
        pass

    #############################################################################

    def get(self, assign_name):
        for statement in self.cst.body:
            if not isinstance(statement, libcst.SimpleStatementLine):
                continue

            if not isinstance(statement.body[0], libcst.Assign):
                continue

            assign = statement.body[0]
            for target in assign.targets:
                if target.target.value != assign_name:
                    continue

                ret = self._parse_node(assign.value)

                if isinstance(ret, dict):
                    ret["assign"] = target.target.value                
                
                return ret

        return None
    
    # Returns a dict from the value node (recursive)
    def _parse_node(self, node):
        if isinstance(node, libcst.Name):
            return self._parse_assigned(node)
        
        elif isinstance(node, libcst.Call):
            return self._parse_call(node)
        
        elif isinstance(node, libcst.Dict):
            return self._parse_dict(node)
        
        elif isinstance(node, libcst.List):
            return self._parse_list(node)

        # Simple statement
        return libcst.parse_module("").code_for_node(node)

    def _parse_call(self, call_node):
        new_value = {
            "name": libcst.parse_module("").code_for_node(call_node.func),
            "arguments": []
        }

        arg_num = { "num": -1 }
        arg_names = self.get_arg_names(new_value["name"])
        if not arg_names:
            arg_names = []
        
        def next_arg_name():
            arg_num["num"] += 1
            if arg_num["num"] >= len(arg_names): 
                return None
            return arg_names[arg_num["num"]]

        for argument in call_node.args:
            new_arg = {
                "value": self._parse_node(argument.value)
            }

            if argument.keyword:
                new_arg["name"] = libcst.parse_module("").code_for_node(argument.keyword)
            else:
                name = next_arg_name()
                if name:
                    new_arg["name"] = name                    

            new_value["arguments"].append(new_arg)

        self.postprocess_call(new_value)

        return new_value
        
    def _parse_dict(self, dict_node):
        new_value = {
            "arguments": []
        }

        for dict_element in dict_node.elements:
            key = dict_element.key.value.strip('\"')
            value = self._parse_node(dict_element.value)
            
            new_value["arguments"].append({
                "name": key,
                "value": value
            })

        return new_value
    
    def _parse_list(self, list_node):
        new_value = []

        for element in list_node.elements:
            new_value.append(
                self._parse_node(element.value)
            )

        return new_value
    
    # Parses an assigned node
    def _parse_assigned(self, name_node):
        assign_node = self._get_assignment(name_node.value)
        assign = libcst.parse_module("").code_for_node(name_node)
        
        if not assign_node:
            return assign
        
        value = self._parse_node(assign_node)
        
        if not isinstance(value, dict):
            return {
                "value": value,
                "assign": assign
            }
        
        value["assign"] = assign
        return value
    
    # Searches for an Assign with the given name and returns its node, or None if not found
    def _get_assignment(self, name):
        assignments = AssignmentExtractor().get(self.cst)
        
        for a in assignments:
            if a["name"] == name:
                return a["node"]
            
        return None
    
