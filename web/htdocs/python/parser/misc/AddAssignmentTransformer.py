import libcst
from .VisitorsWithStack import TransformerWithStack

class AddAssignmentTransformer(TransformerWithStack):
    def __init__(self, name, call_node, insert_before_assign = None, cst = None):
        super().__init__()
        self.cst = cst
        self._count = 0
        
        self.name = name
        self.insert_before_assign = insert_before_assign
        
        self.call_node = call_node

    def leave_Module(self, original_node, updated_node):
        if not self.cst or len(self.cst.body) > 0:
            return updated_node
        
        # In case there is no body, the leave_SimpleStatementLine method is never called
        return updated_node.with_changes(
            body = [
                self._generate_statement()
            ]
        )

    def leave_SimpleStatementLine(self, original_node, updated_node):
        if len(self.stack) != 1:
            return updated_node
        
        if self.insert_before_assign:
            if not isinstance(updated_node.body[0], libcst.Assign):
                return updated_node
            
            assign = updated_node.body[0]
            
            for target in assign.targets:
                if target.target.value == self.insert_before_assign:                
                    return libcst.FlattenSentinel([self._generate_statement(), updated_node])
        else:
            if not self.cst:
                raise Exception("You have to provide a CST to add a statement as last statement")
            
            self._count += 1

            if self._count == len(self.cst.body):
                return libcst.FlattenSentinel([updated_node, self._generate_statement()])
            
        return updated_node        

    def _generate_statement(self):
        return libcst.SimpleStatementLine(
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

    
        
