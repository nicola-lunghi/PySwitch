import libcst
from .VisitorsWithStack import TransformerWithStack

class RemoveDictElementTransformer(TransformerWithStack):
    def __init__(self, node, key):
        super().__init__()

        self.node = node
        self.key = key
        self.removed = None

        self.__node_level = None
        
    def visit_Dict(self, node):
        if node == self.node:
            self.__node_level = len(self.stack)

    def leave_Dict(self, original_node, updated_node):
        if original_node == self.node:
            self.__node_level = None
        
        return updated_node
    
    def leave_DictElement(self, original_node, updated_node):
        if self.__node_level != len(self.stack):
            return updated_node
        
        if updated_node.key.value != self.key:
            return updated_node
        
        self.removed = updated_node
        return libcst.RemoveFromParent()


    
        