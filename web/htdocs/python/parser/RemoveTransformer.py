import libcst

class RemoveTransformer(libcst.CSTTransformer):
    def __init__(self, node):
        super().__init__()

        self.node = node
        self.removed = None
        
    def on_leave(self, original_node, updated_node):
        if original_node == self.node:
            self.removed = original_node
            return libcst.RemoveFromParent()
        
        return super().on_leave(original_node, updated_node)
    
        