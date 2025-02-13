import libcst

class Arguments(libcst.CSTVisitor):
    def __init__(self):
        self.stack = []
        self.result = []
        
    def on_visit(self, node):
        self.stack.append(node)
        
        return super().on_visit(node)

    def on_leave(self, node):
        self.stack.pop()

        super().on_leave(node)

    def visit_Arg(self, node):
        if len(self.stack) != 2:
            return False
        
        self.result.append({
            "name": node.keyword.value,
            "value": self.__format_value(node.value)
        })

        return False

    # Format a value node, depending on its type
    def __format_value(self, value_node):
        if isinstance(value_node, libcst.Name):
            return value_node.value
        
        elif isinstance(value_node, libcst.SimpleString):
            return value_node.value
        
        return libcst.parse_module("").code_for_node(value_node)


