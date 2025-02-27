import libcst
from ..misc.VisitorsWithStack import VisitorWithStack

class Arguments(VisitorWithStack):
    def __init__(self):
        super().__init__()
        self.result = []
        
    def visit_Arg(self, node):
        if len(self.stack) != 2:
            return False

        if not node.keyword:
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


