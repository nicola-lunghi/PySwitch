import libcst

class AddImportsTransformer(libcst.CSTTransformer):
    
    def __init__(self, import_paths):
        self.import_paths = import_paths
        self.__done = False

    def leave_SimpleStatementLine(self, original_node, updated_node):
        if self.__done:
            return updated_node
        
        self.__done = True
        
        new_statements = [
            libcst.parse_statement("from " + definition["importPath"] + " import " + (definition["importName"] if "importName" in definition else definition["name"]) + "\n")
            for definition in self.import_paths
        ]

        return libcst.FlattenSentinel([updated_node] + new_statements)
        