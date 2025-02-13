import libcst

from PySwitchHardware import PySwitchHardware
from .Actions import Actions
from .ActionRemove import ActionRemove
from ..RemoveTransformer import RemoveTransformer

class Input(libcst.CSTVisitor):
    def __init__(self, hw_import_path, port):
        self.port = port
        self.hardwareDefinitions = PySwitchHardware().get(hw_import_path)

        self.__inputs = None
        self.result = None

    # Inputs
    def visit_Assign(self, node):
        if self.result:
            # Already have a reusult
            return False
                
        if node.targets[0].target.value != "Inputs":
            return False
        
        # self.__print("Inputs found")
        self.__inputs = node
        
    def leave_Assign(self, node):
        self.__inputs = None

    # Main Dict of one input
    def visit_Dict(self, node):
        if self.result:
            # Already have a reusult
            return False
                
        if not self.__inputs:
            # Only dicts in the Inputs assign
            return False
        
        if not self.__has_assignment(node):
            # Only inputs assigned to the port
            return False
        
        # self.__print("Assigned input found")
        self.result = node

        return False
    
    ###############################################################################################################################

    # Returns a list containing a result list of nodes, represented by Action instances
    def actions(self, hold = False):
        if not self.result:
            raise Exception("No result to get data from")

        visitor = Actions(hold)
        self.result.visit(visitor)
        return visitor.result

    # Remove action at the given index
    def remove_action(self, index, hold = False):
        if not self.result:
            raise Exception("No result to remove data from")
        
        if index < 0:
            raise Exception("Invalid action index: " + repr(index))

        target_len = len(self.actions()) - 1

        # Get node to remove first
        visitor = ActionRemove(index, hold)
        self.result.visit(visitor)

        if not visitor.result:
            raise Exception("Could not find action at index: " + repr(index))
        
        # Remove the node with a generic remover
        remover = RemoveTransformer(visitor.result)
        self.result = self.result.visit(remover)

        if len(self.actions()) != target_len:
            raise Exception("Failed to remove action: " + repr(index))

    ###############################################################################################################################

    # Checks if an input node has assignment to the given port
    def __has_assignment(self, input):
        for dictElement in input.elements:
            if dictElement.key.value != '"assignment"':
                continue

            definition = self.__get_hw_definition(dictElement.value.value)

            if not definition or "port" not in definition["data"]["model"] or definition["data"]["model"]["port"] != self.port:
                continue            

            return True
        return False
    
    # For a given name, returns the hardware definition
    def __get_hw_definition(self, name):
        for defi in self.hardwareDefinitions:
            if defi["name"] == name:
                return defi
            
