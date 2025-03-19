# from ..PySwitchHardware import PySwitchHardware

# class InputAssignment:
#     def __init__(self, hw_import_path):
#         self.hardwareDefinitions = PySwitchHardware().get(hw_import_path)        
        
#     # Get hardware descriptor. Only returns a value when the node is an input Dict assigned to the port
#     def get(self, node, port):
#         for dict_element in node.elements:
#             if dict_element.key.value != '"assignment"':
#                 continue

#             definition = self.get_by_name(dict_element.value.value)

#             if not definition or "port" not in definition["data"]["model"] or definition["data"]["model"]["port"] != port:
#                 continue
            
#             return definition
        
#         return None
        
#     # Returns the name identifier for a port number
#     def get_by_port(self, port):
#         for defi in self.hardwareDefinitions:
#             if defi["data"]["model"]["port"] == port:
#                 return defi

#     # For a given name, returns the hardware definition
#     def get_by_name(self, name):
#         for defi in self.hardwareDefinitions:
#             if defi["name"] == name:
#                 return defi
            
