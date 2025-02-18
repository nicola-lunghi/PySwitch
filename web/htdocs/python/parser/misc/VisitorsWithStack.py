import libcst

class VisitorWithStack(libcst.CSTVisitor):
    def __init__(self):
        self.stack = []
        
    def on_visit(self, node):
        self.stack.append(node)        
        return super().on_visit(node)

    def on_leave(self, node):
        self.stack.pop()
        return super().on_leave(node)


class TransformerWithStack(libcst.CSTTransformer):
    def __init__(self):
        self.stack = []
        
    def on_visit(self, node):
        self.stack.append(node)        
        return super().on_visit(node)

    def on_leave(self, original_node, updated_node):
        self.stack.pop()
        return super().on_leave(original_node, updated_node)

