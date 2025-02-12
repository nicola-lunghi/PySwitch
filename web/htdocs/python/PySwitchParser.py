import json
import libcst
import libcst.matchers as m
# from libcst.display import dump

from PySwitchHardware import PySwitchHardware


class PySwitchParser:

    # Returns a CST tree for a given source
    def parse(self, source):
        return libcst.parse_module(source)
            
    # Returns unparsed source code for the CST tree passed
    def unparse(self, cst):
        return cst.code
    
    ################################################################################################

    # Returns a JSON list of actions assigned to the switch listening to the given port
    def get_actions(self, hw_import_path, inputs_cst, port):
        ret = {
            "actions": [],
            "actionsHold": []
        }
        
        hardware = PySwitchHardware()
        hardwareDefinitions = hardware.get(hw_import_path)

        class Visitor(libcst.CSTVisitor):
            def __init__(self):
                self.inputs = None
                self.input = None
                self.actions_key = None
            
            # Inputs
            def visit_Assign(self, node):
                if node.targets[0].target.value != "Inputs":
                    return  
                              
                self.inputs = node
                
            def leave_Assign(self, node):
                self.inputs = None

            # Main Dict of one input
            def visit_Dict(self, node):
                if not self.inputs:
                    # Only dicts in the Inputs assign
                    return False
                
                if not self.__has_assignment(node):
                    # Only inputs assigned to the port
                    return False
                
                self.input = node

            def leave_Dict(self, node):
                self.input = None
                
            # Elements of the main input dict
            def visit_DictElement(self, node):
                if not self.input:
                    return
                
                # Store the key
                self.actions_key = node.key.value                

            def leave_DictElement(self, node):
                self.actions_key = None

            # Actions elements
            def visit_Element(self, node):
                if not isinstance(node.value, libcst.Call):
                    return
                
                if self.actions_key == '"actions"':
                    ret["actions"].append({
                        "name": node.value.func.value
                    })
                elif self.actions_key == '"actionsHold"':
                    ret["actionsHold"].append({
                        "name": node.value.func.value
                    })

                return False

            # Checks if an input node has assignment to the given port
            def __has_assignment(self, input):
                for dictElement in input.elements:
                    if dictElement.key.value != '"assignment"':
                        continue

                    definition = self.__get_hw_definition(dictElement.value.value)   
                    if not definition or "port" not in definition["data"]["model"] or definition["data"]["model"]["port"] != port:
                        continue            

                    return True
                return False
            
            # For a given name, returns the hardware definition
            def __get_hw_definition(self, name):
                for defi in hardwareDefinitions:
                    if defi["name"] == name:
                        return defi
                
        inputs_cst.visit(Visitor())

        return json.dumps(ret)
    
    
