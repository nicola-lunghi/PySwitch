import libcst

from .Actions import Actions
from .InputAssignment import InputAssignment
from ..misc.Arguments import Arguments
from ..misc.AddElementTransformer import AddElementTransformer
from ..misc.RemoveDictElementTransformer import RemoveDictElementTransformer

class Input(libcst.CSTVisitor):
    def __init__(self, parser, hw_import_path, port):        
        self.port = port
        
        self.assignment = None
        self.result = None

        self.parser = parser
        self.__inputs = None
        
        self.assignment_handler = InputAssignment(hw_import_path)

        # Buffers
        self.__actions = {}

    # Inputs
    def visit_Assign(self, node):
        if self.result:
            return False
                
        if node.targets[0].target.value != "Inputs":
            return False
        
        self.__inputs = node
        
    def leave_Assign(self, node):
        self.__inputs = None

    # Main Dict of the input
    def visit_Dict(self, node):
        if self.result:
            return False
                
        if not self.__inputs:
            return False
        
        assignment = self.assignment_handler.get(node, self.port)
        if not assignment:
            return False
        
        self.assignment = assignment
        self.result = node

        return False
    
    ###############################################################################################################################

    # Returns the display name
    def display_name(self):
        return self.assignment["displayName"]        

    # Returns hold time
    def hold_time_millis(self):
        return int(self.__get_option("holdTimeMillis", '600'))  # SwitchController.DEFAULT_HOLD_TIME_MILLIS
    
    # Returns hold repeat
    def hold_repeat(self):
        return self.__get_option("holdRepeat", 'False') == 'True'

    # Set hold time in milliseconds
    def set_hold_time_millis(self, time, noUpdate = False):
        self.__set_option(
            name = "holdTimeMillis", 
            value = int(time),
            default = 600, 
            noUpdate = noUpdate
        )

    # Set hold repeat
    def set_hold_repeat(self, repeat, noUpdate = False):
        self.__set_option(
            name = "holdRepeat", 
            value = repeat, 
            default = False, 
            noUpdate = noUpdate
        )

    ###############################################################################################################################

    # Returns a list containing a result list of nodes, represented by Action instances
    def actions(self, hold = False):
        if not self.result:
            raise Exception("No result to get data from")

        if hold in self.__actions:
            return self.__actions[hold]

        visitor = Actions(self, hold)
        self.result.visit(visitor)
        self.__actions[hold] = visitor.result

        return self.__actions[hold]

    # Overwrites all actions from the passed definition list
    def set_actions(self, actions, hold = False, noUpdate = False):
        if not self.result:
            raise Exception("No result loaded to modify")
        
        # Remove old actions list
        remover = RemoveDictElementTransformer(
            node = self.result,
            key = '"actions"' if not hold else '"actionsHold"'
        )
        self.result = self.result.visit(remover)
        
        def get_arg_value(definition, arg_index):            
            return Arguments(definition.name).parse_value(definition.arguments[arg_index].name, definition.arguments[arg_index].value)

        def get_element_value_node(definition):
            call = libcst.Call(
                func = libcst.parse_expression(definition.name),
                    # libcst.Name(
                    #     value = definition.name,                        
                    # ),

                whitespace_before_args = libcst.ParenthesizedWhitespace(
                    first_line = libcst.TrailingWhitespace(
                        whitespace = libcst.SimpleWhitespace(value=''),
                        comment = None,
                        newline = libcst.Newline(),
                    ),
                    empty_lines=[],
                    indent=True,
                    last_line = libcst.SimpleWhitespace(value='                ')
                ),

                args = [
                    libcst.Arg(
                        keyword = libcst.Name(
                            value = definition.arguments[arg_index].name
                        ),
                        value = get_arg_value(definition, arg_index),
                        whitespace_after_arg = libcst.ParenthesizedWhitespace(
                            first_line = libcst.TrailingWhitespace(
                                whitespace = libcst.SimpleWhitespace(value=''),
                                comment = None,
                                newline = libcst.Newline(),
                            ),
                            empty_lines=[],
                            indent=True,
                            last_line = libcst.SimpleWhitespace(
                                value = '                ' if (arg_index < len(definition.arguments) - 1) else '            '
                            )
                        )
                    )
                    for arg_index in range(len(definition.arguments))
                ]
            )

            if "assign" in definition.to_py() and definition.assign:
                self.parser.set_assignment(definition.assign, call, "inputs_py", "Inputs")

                return libcst.Name(
                    value = definition.assign
                )
            else:
                return call            

        # Add new actions list
        elements = [
            libcst.Element(
                value = get_element_value_node(definition),

                comma = libcst.Comma(
                    whitespace_after = libcst.ParenthesizedWhitespace(
                        first_line = libcst.TrailingWhitespace(
                            whitespace = libcst.SimpleWhitespace(value=''),
                            comment = None,
                            newline = libcst.Newline(),
                        ),
                        empty_lines=[],
                        indent=True,
                        last_line = libcst.SimpleWhitespace(value='            ')
                    )
                )

            )
            for definition in actions
        ]
        
        adder = AddElementTransformer(
            node = self.result,
            new_element = libcst.DictElement(
                key = libcst.SimpleString(
                    value = '"actions"' if not hold else '"actionsHold"'
                ),
                value = libcst.List(
                    elements = elements,
                    
                    lbracket = libcst.LeftSquareBracket(
                        whitespace_after = libcst.ParenthesizedWhitespace(
                            first_line = libcst.TrailingWhitespace(
                                whitespace = libcst.SimpleWhitespace(value=''),
                                newline = libcst.Newline()
                            ),
                            indent=True,
                            last_line = libcst.SimpleWhitespace(value='            ')
                        )
                    ),

                    rbracket = libcst.RightSquareBracket(
                        whitespace_before = libcst.ParenthesizedWhitespace(
                            first_line = libcst.TrailingWhitespace(
                                whitespace = libcst.SimpleWhitespace(value=''),
                                newline = libcst.Newline()
                            ),
                            indent=True,
                            last_line = libcst.SimpleWhitespace(value='        ')
                        )
                    )
                )
            )
        )

        self.result = self.result.visit(adder)

        # Reset buffer
        self.__actions = {}

        # Tell the parser to replace the new state of this input in its CST buffers
        self.parser.update_input(self, noUpdate)

    ###############################################################################################################################

    # Parse one option from the dict node
    def __get_option(self, name, default):
        if not self.result:
            raise Exception("No result to get options from")

        for element in self.result.elements:
            if element.key.value == '"' + name + '"':
                return libcst.parse_module("").code_for_node(element.value)
            
        return default

    # Sets an option in the dict node
    def __set_option(self, name, value, default, noUpdate):
        remover = RemoveDictElementTransformer(
            node = self.result,
            key = '"' + name + '"'
        )
        self.result = self.result.visit(remover)

        if value != default:
            adder = AddElementTransformer(
                node = self.result,
                new_element = libcst.DictElement(
                    key = libcst.SimpleString(
                        value = '"' + name + '"'
                    ),
                    value = libcst.parse_expression(str(value)),
                    comma = libcst.Comma(
                        whitespace_after = libcst.ParenthesizedWhitespace(
                            first_line = libcst.TrailingWhitespace(
                                newline = libcst.Newline()
                            ),
                            last_line = libcst.SimpleWhitespace(
                                value='        '
                            )
                        )
                    )
                )
            )
            self.result = self.result.visit(adder)

        # Tell the parser to replace the new state of this input in its CST buffers
        self.parser.update_input(self, noUpdate)

    # ###############################################################################################################################

    # # Remove an action, from the actions or the actionsHold trees. Called by Action.remove (which is 
    # # the one to call if you use the parser from JS!)
    # def remove_action(self, action_node):
    #     if not self.result:
    #         raise Exception("No result to remove data from")
        
    #     # We want to check if the operation has been successful
    #     target_len = len(self.actions()) - 1
    #     target_len_hold = len(self.actions(True)) - 1
        
    #     # Remove the node
    #     self.result = self.result.deep_remove(action_node)

    #     if not (len(self.actions()) != target_len or len(self.actions(True)) != target_len_hold):
    #         raise Exception("Failed to remove action")
        
    #     # Tell the parser to replace the new state of this input in its CST buffers
    #     self.parser.update_input(self)

    # ###############################################################################################################################

    # # Adds an action to the input. If index is None, the action is  
    # # appended to the end of the list.
    # def add_action(self, definition, hold = False, index = None):
    #     if not self.result:
    #         raise Exception("No result to add data to")
        
    #     # We want to check if the operation has been successful
    #     target_len = len(self.actions()) + 1
    #     target_len_hold = len(self.actions(True)) + 1

    #     # Get the parent dict entry (actions or actionsHold)
    #     visitor = Actions(self, hold)
    #     self.result.visit(visitor)
    
    #     new_element = libcst.Element(
    #         value = libcst.Call(
    #             func = libcst.Name(
    #                 value = definition.name
    #             ),
    #             args = [
    #                 libcst.Arg(
    #                     keyword = libcst.Name(
    #                         value = a.name
    #                     ),
    #                     value = libcst.parse_expression(a.value)
    #                 )
    #                 for a in definition.arguments]
    #         )
    #     )
    
    #     if not visitor.actions_list:
    #         # Actions entry not present: Create one
    #         adder = AddElementTransformer(
    #             node = self.result,
    #             new_element = libcst.DictElement(
    #                 key = libcst.SimpleString(
    #                     value = '"actions"' if not hold else '"actionsHold"'
    #                 ),
    #                 value = libcst.List(
    #                     elements = [
    #                         new_element
    #                     ]
    #                 )
    #             ),
    #             index = index
    #         )
    #     else:
    #         # Add to existing actions list
    #         adder = AddElementTransformer(
    #             node = visitor.actions_list,
    #             new_element = new_element,
    #             index = index
    #         )
            
    #     self.result = self.result.visit(adder)
        
    #     if not (len(self.actions()) != target_len or len(self.actions(True)) != target_len_hold):
    #         raise Exception("Failed to add action")
        
    #     # Tell the parser to replace the new state of this input in its CST buffers
    #     self.parser.update_input(self)