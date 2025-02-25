import libcst

from .CollectCommentsTransformer import CollectCommentsTransformer

class ClassAttributeExtractor:

    def __init__(self, file, className, importPath):
        self.file = file
        self.className = className
        self.importPath = importPath

    # Returns a list of all public functions defined on module level
    def get(self):
        ret = []

        with open(self.file) as f: content = f.read()

        # Parse code of definition file
        cst = libcst.parse_module(content)
        
        # Collect the comment string, in any, for a node
        def get_comments(node, level = None):
            visitor = CollectCommentsTransformer(level)
            node.visit(visitor)
            return visitor.comment

        # Get parameters list
        def get_params(statement):
            params = []

            for param in statement.params.params:
                params.append({
                    "name": param.name.value,
                    "default": libcst.parse_module("").code_for_node(param.default) if param.default else None,
                    "comment": get_comments(param)
                })

            return params

        class ClassVisitor(libcst.CSTVisitor):
            def __init__(self, main):
                self.inside_classdef = False
                self.main = main

            def visit_ClassDef(self, node):
                if node.name.value != self.main.className:
                    return False
                
                self.inside_classdef = True

            def leave_ClassDef(self, node):
                self.inside_classdef = False

            def visit_FunctionDef(self, node):
                if not self.inside_classdef: 
                    return False
                
                if node.name.value.startswith("_"):
                    return False
                
                ret.append({
                    "name": self.main.className + "." + node.name.value,
                    "parameters": get_params(node),
                    "comment": get_comments(node, 0),
                    "importPath": self.main.importPath,
                    "importName": self.main.className
                })

        cst.visit(ClassVisitor(self))

        # # Check all statements for function definitions
        # for statement in cst.body:
        #     if not isinstance(statement, libcst.FunctionDef):
        #         continue

        #     if statement.name.value.startswith("_"):
        #         continue

        #     ret.append({
        #         "name": statement.name.value,
        #         "parameters": get_params(statement),
        #         "comment": get_comments(statement, 0),
        #         "importPath": path.replace("/", ".").removesuffix(".py")
        #     })

        return ret