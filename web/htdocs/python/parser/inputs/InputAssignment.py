from ..PySwitchHardware import PySwitchHardware

class InputAssignment:
    def __init__(self, hw_import_path):
        self.hardwareDefinitions = PySwitchHardware().get(hw_import_path)        
        
    # Get hardware descriptor. Only returns a value when the node is an input Dict assigned to the port
    def get(self, node, port):
        for dictElement in node.elements:
            if dictElement.key.value != '"assignment"':
                continue

            definition = self.__get_hw_definition(dictElement.value.value)

            if not definition or "port" not in definition["data"]["model"] or definition["data"]["model"]["port"] != port:
                continue
            
            return definition
        
        return None
        
    # For a given name, returns the hardware definition
    def __get_hw_definition(self, name):
        for defi in self.hardwareDefinitions:
            if defi["name"] == name:
                return defi
            
