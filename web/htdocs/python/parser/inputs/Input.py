import libcst
# from libcst.display import dump

from .Actions import Actions
from .ActionFinder import ActionFinder
from .InputAssignment import InputAssignment
from ..RemoveTransformer import RemoveTransformer

class Input(libcst.CSTVisitor):
    def __init__(self, hw_import_path, port):
        self.port = port
        self.assignment = InputAssignment(hw_import_path)

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
        
        if not self.assignment.has_assignment(node, self.port):
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

    # Remove action at the given index. 
    # Note that after this, you have to update the CST.
    def remove_action(self, index, hold = False):
        if not self.result:
            raise Exception("No result to remove data from")
        
        if index < 0:
            raise Exception("Invalid action index: " + repr(index))

        target_len = len(self.actions()) - 1

        # Get node to remove first
        visitor = ActionFinder(index, hold)
        self.result.visit(visitor)

        if not visitor.result:
            raise Exception("Could not find action at index: " + repr(index))
        
        # Remove the node with a generic remover
        remover = RemoveTransformer(visitor.result)
        self.result = self.result.visit(remover)

        if len(self.actions()) != target_len:
            raise Exception("Failed to remove action: " + repr(index))
