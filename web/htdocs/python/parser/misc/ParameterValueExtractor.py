import libcst

# Returns all parameters which have the passed value
class ParameterValueExtractor(libcst.CSTVisitor):
        
    def __init__(self, value):
        self.param_value = value
        self.result = []

    def visit_Arg(self, node):
        if not isinstance(node.value, libcst.Name):
            return 
        
        if node.value.value != self.param_value:
            return 
        
        self.result.append(node)

        
