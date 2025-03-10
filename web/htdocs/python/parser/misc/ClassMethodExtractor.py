import libcst

from .CollectCommentsTransformer import CollectCommentsTransformer

class ClassMethodExtractor:

    def __init__(self, file, className, importPath, include_underscore = False):
        self.file = file
        self.className = className
        self.importPath = importPath
        self.include_underscore = include_underscore        

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
                if param.name.value == "self": 
                    continue
                
                params.append({
                    "name": param.name.value,
                    "default": libcst.parse_module("").code_for_node(param.default) if param.default else None,
                    "comment": get_comments(param)
                })

            return params

        class ClassVisitor(libcst.CSTVisitor):
            def __init__(self, main):
                self.main = main

                self.classdef_depth = None
                self.class_stack = 0

            def visit_ClassDef(self, node):
                self.class_stack += 1

                if node.name.value != self.main.className:
                    return False
                                
                self.classdef_depth = self.class_stack

            def leave_ClassDef(self, node):
                self.class_stack -= 1

            def visit_FunctionDef(self, node):
                if not self.class_stack == self.classdef_depth: 
                    return False
                
                if not self.main.include_underscore and node.name.value.startswith("_"):
                    return False
                
                ret.append({
                    "name": self.main.className + (("." + node.name.value) if node.name.value != "__init__" else ""),
                    "parameters": get_params(node),
                    "comment": get_comments(node, 0),
                    "importPath": self.main.importPath,
                    "importName": self.main.className
                })

        cst.visit(ClassVisitor(self))

        return ret