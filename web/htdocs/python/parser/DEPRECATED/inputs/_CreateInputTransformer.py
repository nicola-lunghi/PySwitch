# import libcst

# from .InputAssignment import InputAssignment
# from ..misc.VisitorsWithStack import TransformerWithStack

# class CreateInputTransformer(TransformerWithStack):
#     def __init__(self, hw_import_path, port):
#         super().__init__()

#         self.port = port        
#         self.assignment_handler = InputAssignment(hw_import_path)
#         self.done = False    

#         self.__inputs_level = None    

#     # Inputs
#     def visit_Assign(self, node):
#         if self.done:
#             return False
                
#         if node.targets[0].target.value != "Inputs": # type: ignore
#             return False
        
#         self.__inputs_level = len(self.stack)
        
#     def leave_Assign(self, original_node, updated_node):
#         self.__inputs_level = None
#         return updated_node

#     # Inputs
#     def leave_List(self, original_node, updated_node):
#         if self.done:
#             return updated_node
        
#         if self.__inputs_level != len(self.stack):
#             return updated_node
                
#         definition = self.assignment_handler.get_by_port(self.port)
        
#         def sort_func(item):
#             for dict_element in item.value.elements:
#                 if dict_element.key.value != '"assignment"':
#                     continue

#                 return dict_element.value.value     # Assignment value
            
#             return "XXXXXXXXXXXXXXXXXXXXXX"

#         ret = updated_node.with_changes(
#             elements = [
#                 libcst.Element(
#                     value = libcst.Dict(
#                         elements = [
#                             libcst.DictElement(
#                                 key = libcst.SimpleString(
#                                     value = '"assignment"'
#                                 ),
#                                 value = libcst.Name(
#                                     value = definition["name"]
#                                 ),
#                                 comma = libcst.Comma(
#                                     whitespace_before = libcst.SimpleWhitespace(value=''),
#                                     whitespace_after = libcst.ParenthesizedWhitespace(
#                                         first_line = libcst.TrailingWhitespace(
#                                             whitespace = libcst.SimpleWhitespace(value=''),
#                                             newline = libcst.Newline(),
#                                         ),
#                                         last_line = libcst.SimpleWhitespace(value='        ')
#                                     )
#                                 )
#                             )                        
#                         ]
#                     ),

#                     comma = libcst.Comma(
#                         whitespace_after = libcst.ParenthesizedWhitespace(
#                             first_line = libcst.TrailingWhitespace(
#                                 whitespace = libcst.SimpleWhitespace(value=''),
#                                 comment = None,
#                                 newline = libcst.Newline(),
#                             ),
#                             empty_lines=[],
#                             indent=True,
#                             last_line = libcst.SimpleWhitespace(value='    ')
#                         )
#                     )
#                 )
#             ] + [e for e in updated_node.elements]
#         )

#         self.done = True
#         return ret
        