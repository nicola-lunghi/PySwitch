import libcst

# class PySwitchCstVisitor(libcst.CSTVisitor):
#     def on_visit(self, node):
#         print(node)

#     def on_visit_attribute(self, node, attribute):
#         pass #print(attribute)

class PySwitchParser:
    def parse(self, source):
        cst = libcst.parse_module(source)
        # cst.visit(PySwitchCstVisitor())

        # if not isinstance(bodyline, libcst.SimpleStatementLine):
        #     continue

        # assign = bodyline.body[0]
        # if not isinstance(assign, libcst.Assign):
        #     continue

        # if assign.targets[0].target.value != "Inputs":
        #     continue

        # if isinstance(assign.value, libcst.List):
        #     continue

        # # for input in assign.value.elements:
        # #     print()

        return cst
            
    def unparse(self, cst):
        return cst.code
    