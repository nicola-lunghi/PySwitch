# import libcst

# class Pager(libcst.CSTVisitor):
#     def __init__(self, parser):
#         self.name = None
#         self.parser = parser

#     # Inputs
#     def visit_Assign(self, node):
#         if self.name:
#             return False
                
#         if not isinstance(node.value, libcst.Call):
#             return False
        
#         if not isinstance(node.value.func, libcst.Name):
#             return False
        
#         if not node.value.func.value == "PagerAction":
#             return False
        
#         self.name = node.targets[0].target.value

#     # def leave_Assign(self, node):
#     #     pass

