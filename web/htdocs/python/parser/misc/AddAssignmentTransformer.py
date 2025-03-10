import libcst
from .VisitorsWithStack import TransformerWithStack

class AddAssignmentTransformer(TransformerWithStack):
    def __init__(self, name, call_node):
        super().__init__()
        self.name = name
        
        self.call_node = call_node

    def leave_SimpleStatementLine(self, original_node, updated_node):
        if len(self.stack) != 1:
            return updated_node
        
        if not isinstance(updated_node.body[0], libcst.Assign):
            return updated_node
        
        assign = updated_node.body[0]
        
        for target in assign.targets:
            if target.target.value == "Inputs":
                new_statement = libcst.SimpleStatementLine(
                    body = [
                        libcst.Assign(
                            targets = [
                                libcst.AssignTarget(
                                    target = libcst.Name(value = self.name),
                                    whitespace_before_equal = libcst.SimpleWhitespace(value=' '),
                                    whitespace_after_equal = libcst.SimpleWhitespace(value=' ')
                                )
                            ],
                            value = self.call_node                    
                        )
                    ],

                    leading_lines=[
                        libcst.EmptyLine(                            
                            whitespace = libcst.SimpleWhitespace(value=''),                            
                            newline = libcst.Newline()
                        )
                    ],

                    trailing_whitespace = libcst.TrailingWhitespace(
                        whitespace = libcst.SimpleWhitespace(value=''),
                        newline = libcst.Newline()
                    )
                )

                return libcst.FlattenSentinel([new_statement, updated_node])
            
        return updated_node        


    
        
