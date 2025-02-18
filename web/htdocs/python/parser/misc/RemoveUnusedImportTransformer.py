import libcst
from collections import defaultdict

# https://libcst.readthedocs.io/en/latest/scope_tutorial.html
class RemoveUnusedImportTransformer(libcst.CSTTransformer):
    def __init__(self, wrapper):
        scopes = set(wrapper.resolve(libcst.metadata.ScopeProvider).values())

        self.unused_imports = defaultdict(set)
        
        for scope in scopes:
            for assignment in scope.assignments:
                node = assignment.node

                if isinstance(assignment, libcst.metadata.Assignment) and isinstance(node, (libcst.Import, libcst.ImportFrom)):
                    if len(assignment.references) == 0:
                        self.unused_imports[node].add(assignment.name)

    def _leave_import_alike(self, original_node, updated_node):
        if original_node not in self.unused_imports:
            return updated_node        
        
        names_to_keep = []
        for name in updated_node.names:
            asname = name.asname
            if asname is not None:
                name_value = asname.name.value
            else:
                name_value = name.name.value
            if name_value not in self.unused_imports[original_node]:
                names_to_keep.append(name.with_changes(comma=libcst.MaybeSentinel.DEFAULT))
        
        if len(names_to_keep) == 0:
            return libcst.RemoveFromParent()
        else:
            return updated_node.with_changes(names=names_to_keep)

    def leave_Import(self, original_node, updated_node):
        return self._leave_import_alike(original_node, updated_node)

    def leave_ImportFrom(self, original_node, updated_node):
        return self._leave_import_alike(original_node, updated_node)
    