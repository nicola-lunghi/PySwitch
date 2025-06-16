import libcst

class ClassNameExtractor:

    def __init__(self, file, import_path, include_underscore = False):
        self.file = file
        self.import_path = import_path
        self.include_underscore = include_underscore        

    # Returns a list of all public classes defined on module level
    def get(self):
        ret = []

        with open(self.file) as f: content = f.read()
        
        # Parse code of definition file
        cst = libcst.parse_module(content)
        
        class ClassVisitor(libcst.CSTVisitor):
            def __init__(self, main):
                self.main = main

            def visit_ClassDef(self, node):
                ret.append({
                    "name": node.name.value,
                    "importPath": self.main.import_path
                })

        cst.visit(ClassVisitor(self))

        return ret