import libcst
from .VisitorsWithStack import TransformerWithStack

class RemoveAssignmentTransformer(TransformerWithStack):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def leave_Assign(self, original_node, updated_node):
        if len(self.stack) != 2:
            return updated_node
        
        for target in updated_node.targets:
            if target.target.value == self.name:
                return libcst.RemoveFromParent()      
            
        return updated_node        


    
        
