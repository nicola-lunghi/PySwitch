import libcst

from .CollectCommentsTransformer import CollectCommentsTransformer

class FunctionExtractor:

    def __init__(self, import_paths):
        self.import_paths = import_paths

    # Returns a list of all public functions defined on module level
    def get(self):
        ret = []

        for path in self.import_paths:
            with open(path) as f: content = f.read()

            # Parse code of definition file
            cst = libcst.parse_module(content)
            
            # Collect the comment string, in any, for a Param node
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

            # Check all statements for function definitions
            for statement in cst.body:
                if not isinstance(statement, libcst.FunctionDef):
                    continue

                if statement.name.value.startswith("_"):
                    continue

                ret.append({
                    "name": statement.name.value,
                    "parameters": get_params(statement),
                    "comment": get_comments(statement, 0),
                    "importPath": path.replace("/", ".").removesuffix(".py")
                })

        return ret