import libcst

class InputReplacer(libcst.CSTTransformer):
    def __init__(self, input):
        super().__init__()

        self.input = input
        self.__inputs = None
        self.replaced = None

    # Inputs
    def visit_Assign(self, node):
        if self.replaced:
            # Already have a reusult
            return False
                
        if node.targets[0].target.value != "Inputs":
            return False
        
        self.__inputs = node
        
    def leave_Assign(self, original_node, updated_node):
        self.__inputs = None
        return updated_node

    # Main Dict of one input
    def leave_Dict(self, original_node, updated_node):
        if self.replaced:
            # Already have a reusult
            return updated_node
                
        if not self.__inputs:
            # Only dicts in the Inputs assign
            return updated_node
        
        if not self.input.assignment.has_assignment(updated_node, self.input.port):
            # Only inputs assigned to the port of the input to be replaced
            return updated_node
        
        self.replaced = updated_node
        return self.input.result
        