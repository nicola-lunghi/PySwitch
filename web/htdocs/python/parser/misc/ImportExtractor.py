import libcst

class ImportExtractor(libcst.CSTVisitor):
        
    def __init__(self, name):
        self.import_name = name
        self.result = None

    def _visit_import_alike(self, node):
        if self.result:
            return False

        if isinstance(node.names, libcst.ImportStar):
            return False

        for name in node.names:
            asname = name.asname
            if asname is not None:
                name_value = asname.name.value
            else:
                name_value = name.name.value
            
            if name_value == self.import_name:
                self.result = libcst.parse_module("").code_for_node(node)

        return False

    def visit_Import(self, node):
        return self._visit_import_alike(node)

    def visit_ImportFrom(self, node):
        return self._visit_import_alike(node)