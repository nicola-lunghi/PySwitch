import libcst

from .Actions import Actions
from .InputAssignment import InputAssignment
from ..AddElementTransformer import AddElementTransformer

class Input(libcst.CSTVisitor):
    def __init__(self, parser, hw_import_path, port):        
        self.port = port
        self.assignment = InputAssignment(hw_import_path)
        self.result = None
        self.__parser = parser
        self.__inputs = None
        
    # Inputs
    def visit_Assign(self, node):
        if self.result:
            # Already have a result
            return False
                
        if node.targets[0].target.value != "Inputs":
            return False
        
        self.__inputs = node
        
    def leave_Assign(self, node):
        self.__inputs = None

    # Main Dict of one input
    def visit_Dict(self, node):
        if self.result:
            # Already have a result
            return False
                
        if not self.__inputs:
            # Only dicts in the Inputs assign
            return False
        
        if not self.assignment.has_assignment(node, self.port):
            # Only inputs assigned to the port
            return False
        
        # self.__print("Assigned input found")
        self.result = node

        return False
    
    ###############################################################################################################################

    # Returns a list containing a result list of nodes, represented by Action instances
    def actions(self, hold = False):
        if not self.result:
            raise Exception("No result to get data from")

        visitor = Actions(self, hold)
        self.result.visit(visitor)
        return visitor.result

    ###############################################################################################################################

    # Remove an action, from the actions or the actionsHold trees. Called by Action.remove (which is 
    # the one to call if you use the parser from JS!)
    def remove_action(self, action_node):
        if not self.result:
            raise Exception("No result to remove data from")
        
        # We want to check if the operation has been successful
        target_len = len(self.actions()) - 1
        target_len_hold = len(self.actions(True)) - 1
        
        # Remove the node
        self.result = self.result.deep_remove(action_node)

        if not (len(self.actions()) != target_len or len(self.actions(True)) != target_len_hold):
            raise Exception("Failed to remove action")
        
        # Tell the parser to replace the new state of this input in its CST buffers
        self.__parser.update_input(self)

    ###############################################################################################################################

    # Adds an action to the input. If index is None, the action is  
    # appended to the end of the list.
    def add_action(self, definition, hold = False, index = None):
        if not self.result:
            raise Exception("No result to remove data from")
        
        # We want to check if the operation has been successful
        target_len = len(self.actions()) + 1
        target_len_hold = len(self.actions(True)) + 1

        # Get the parent dict entry (actions or actionsHold)
        visitor = Actions(self, hold)
        self.result.visit(visitor)
    
        new_element = libcst.Element(
            value = libcst.Call(
                func = libcst.Name(
                    value = definition.name
                ),
                args = [
                    libcst.Arg(
                        keyword = libcst.Name(
                            value = a.name
                        ),
                        value = libcst.parse_expression(a.value)
                    )
                    for a in definition.arguments]
            )
        )
    
        if not visitor.actions_list:
            # Actions entry not present: Create one
            adder = AddElementTransformer(
                node = self.result,
                new_element = libcst.DictElement(
                    key = libcst.SimpleString(
                        value = '"actions"' if not hold else '"actionsHold"'
                    ),
                    value = libcst.List(
                        elements = [
                            new_element
                        ]
                    )
                ),
                index = index
            )
        else:
            # Add to existing actions list
            adder = AddElementTransformer(
                node = visitor.actions_list,
                new_element = new_element,
                index = index
            )
            
        self.result = self.result.visit(adder)
        
        if not (len(self.actions()) != target_len or len(self.actions(True)) != target_len_hold):
            raise Exception("Failed to add action")
        
        # Tell the parser to replace the new state of this input in its CST buffers
        self.__parser.update_input(self)