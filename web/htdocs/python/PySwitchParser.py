import json
import libcst

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
    def get_actions(self, hw_import_path, inputs_cst, port, hold = False):
        ret = []

        hardware = PySwitchHardware()
        hardwareDefinitions = hardware.get(hw_import_path)

        actions_token = '"actions"' if not hold else '"actionsHold"'

        for bodyline in inputs_cst.body:
            if not isinstance(bodyline, libcst.SimpleStatementLine):
                continue
            
            assign = bodyline.body[0]
            if not isinstance(assign, libcst.Assign) or assign.targets[0].target.value != "Inputs":
                continue
            
            if not isinstance(assign.value, libcst.List):
                continue

            # Inputs list
            for input in assign.value.elements:
                if not isinstance(input.value, libcst.Dict) or not self.__has_assignment(hardwareDefinitions, input, port):
                    continue

                # Input elements assigned to the port
                for dictElement in input.value.elements:                    
                    if dictElement.key.value != actions_token or not isinstance(dictElement.value, libcst.List):
                        continue
                    
                    # Actions
                    for action in dictElement.value.elements:
                        if not isinstance(action.value, libcst.Call):
                            continue

                        ret.append({
                            "name": action.value.func.value
                        })
                        
        return json.dumps(ret)
    
    # Checks if an input node has assignment to the given port
    def __has_assignment(self, hardwareDefinitions, input, port):
        for dictElement in input.value.elements:
            if dictElement.key.value != '"assignment"':
                continue

            definition = self.__get_hw_definition(hardwareDefinitions, dictElement.value.value)   
            if not definition or "port" not in definition["data"]["model"] or definition["data"]["model"]["port"] != port:
                continue            

            return True
        return False
    
    # For a given name, returns the hardware definition
    def __get_hw_definition(self, hardwareDefinitions, name):
        for defi in hardwareDefinitions:
            if defi["name"] == name:
                return defi
                