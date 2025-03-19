from .VisitorsWithStack import TransformerWithStack

class ReplaceAssignmentTransformer(TransformerWithStack):
    def __init__(self, name, node):
        super().__init__()
        self.name = name
        self.node = node
        self.replaced = False

    def leave_Assign(self, original_node, updated_node):
        if len(self.stack) != 2:
            return updated_node
        
        for target in updated_node.targets:
            if target.target.value == self.name:
                self.replaced = True
                return updated_node.with_changes(
                    value = self.node
                )
            
        return updated_node


    
        
