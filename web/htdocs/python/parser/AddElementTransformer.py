import libcst

class AddElementTransformer(libcst.CSTTransformer):
    def __init__(self, node, new_element, index = None):
        super().__init__()

        self.node = node
        self.new_element = new_element
        self.index = index
  
    def on_leave(self, original_node, updated_node):
        if original_node == self.node:
            elements = updated_node.elements

            new_elements = [e for e in elements]
            new_elements.insert(self.index if self.index != None else len(new_elements), self.new_element)

            return updated_node.with_changes(
                elements = new_elements
            )
        
        return super().on_leave(original_node, updated_node)
    
        