from ..PySwitchHardware import PySwitchHardware

class InputAssignment:
    def __init__(self, hw_import_path):
        self.hardwareDefinitions = PySwitchHardware().get(hw_import_path)
        
    # Checks if an input node has assignment to the given port
    def has_assignment(self, input, port):
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
        for defi in self.hardwareDefinitions:
            if defi["name"] == name:
                return defi
            
