import libcst

from .SplashElements import SplashElements
# from .Arguments import Arguments
# from .InputAssignment import InputAssignment

class Splashes(libcst.CSTVisitor):
    def __init__(self, parser):        
        self.parser = parser
        self.result = None

        # Buffers
        self.__elements = None
        
    def visit_Assign(self, node):
        if self.result:
            return False

        if node.targets[0].target.value == "Splashes":
            self.result = node
            self.name = self._extract_name(node.value)
        
        return False

    # Extract the call name     
    def _extract_name(self, node):
        if isinstance(node, libcst.Call):        
            return node.func.value
        
        return None
    
    # Returns a list containing a result list of nodes, represented by SplashElement instances
    def elements(self):
        if not self.result:
            raise Exception("No result to get data from")

        if self.__elements:
            return self.__elements

        visitor = SplashElements(self.parser)
        self.result.visit(visitor)
        self.__elements = visitor.result

        return self.__elements

    # Overwrites all elements from the passed definition list
    def set_elements(self, elements, noUpdate = False):
        if not self.result:
            raise Exception("No result loaded to modify")
        
        # # Remove old actions list
        # remover = RemoveDictElementTransformer(
        #     node = self.result,
        #     key = '"actions"' if not hold else '"actionsHold"'
        # )
        # self.result = self.result.visit(remover)
        
        # def get_arg_value(definition, arg_index):            
        #     return Arguments(definition.name).parse_value(definition.arguments[arg_index].name, definition.arguments[arg_index].value)

        # def get_element_value_node(definition):
        #     call = libcst.Call(
        #         func = libcst.parse_expression(definition.name),
        #             # libcst.Name(
        #             #     value = definition.name,                        
        #             # ),

        #         whitespace_before_args = libcst.ParenthesizedWhitespace(
        #             first_line = libcst.TrailingWhitespace(
        #                 whitespace = libcst.SimpleWhitespace(value=''),
        #                 comment = None,
        #                 newline = libcst.Newline(),
        #             ),
        #             empty_lines=[],
        #             indent=True,
        #             last_line = libcst.SimpleWhitespace(value='                ')
        #         ),

        #         args = [
        #             libcst.Arg(
        #                 keyword = libcst.Name(
        #                     value = definition.arguments[arg_index].name
        #                 ),
        #                 value = get_arg_value(definition, arg_index),
        #                 whitespace_after_arg = libcst.ParenthesizedWhitespace(
        #                     first_line = libcst.TrailingWhitespace(
        #                         whitespace = libcst.SimpleWhitespace(value=''),
        #                         comment = None,
        #                         newline = libcst.Newline(),
        #                     ),
        #                     empty_lines=[],
        #                     indent=True,
        #                     last_line = libcst.SimpleWhitespace(
        #                         value = '                ' if (arg_index < len(definition.arguments) - 1) else '            '
        #                     )
        #                 )
        #             )
        #             for arg_index in range(len(definition.arguments))
        #         ]
        #     )

        #     if "assign" in definition.to_py() and definition.assign:
        #         self.parser.set_action_assignment(definition.assign, call)

        #         return libcst.Name(
        #             value = definition.assign
        #         )
        #     else:
        #         return call            

        # # Add new actions list
        # elements = [
        #     libcst.Element(
        #         value = get_element_value_node(definition),

        #         comma = libcst.Comma(
        #             whitespace_after = libcst.ParenthesizedWhitespace(
        #                 first_line = libcst.TrailingWhitespace(
        #                     whitespace = libcst.SimpleWhitespace(value=''),
        #                     comment = None,
        #                     newline = libcst.Newline(),
        #                 ),
        #                 empty_lines=[],
        #                 indent=True,
        #                 last_line = libcst.SimpleWhitespace(value='            ')
        #             )
        #         )

        #     )
        #     for definition in actions
        # ]
        
        # adder = AddElementTransformer(
        #     node = self.result,
        #     new_element = libcst.DictElement(
        #         key = libcst.SimpleString(
        #             value = '"actions"' if not hold else '"actionsHold"'
        #         ),
        #         value = libcst.List(
        #             elements = elements,
                    
        #             lbracket = libcst.LeftSquareBracket(
        #                 whitespace_after = libcst.ParenthesizedWhitespace(
        #                     first_line = libcst.TrailingWhitespace(
        #                         whitespace = libcst.SimpleWhitespace(value=''),
        #                         newline = libcst.Newline()
        #                     ),
        #                     indent=True,
        #                     last_line = libcst.SimpleWhitespace(value='            ')
        #                 )
        #             ),

        #             rbracket = libcst.RightSquareBracket(
        #                 whitespace_before = libcst.ParenthesizedWhitespace(
        #                     first_line = libcst.TrailingWhitespace(
        #                         whitespace = libcst.SimpleWhitespace(value=''),
        #                         newline = libcst.Newline()
        #                     ),
        #                     indent=True,
        #                     last_line = libcst.SimpleWhitespace(value='        ')
        #                 )
        #             )
        #         )
        #     )
        # )

        # self.result = self.result.visit(adder)

        # # Reset buffer
        # self.__actions = {}

        # # Tell the parser to replace the new state of this input in its CST buffers
        # self.parser.update_input(self, noUpdate)

