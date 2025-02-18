import libcst

from .inputs.Input import Input
from .inputs.InputReplacer import InputReplacer
from .misc.RemoveUnusedImportTransformer import RemoveUnusedImportTransformer

class PySwitchParser:

    def __init__(self, hw_import_path):
        self.__hw_import_path = hw_import_path       
        self.__csts = None

    # Set the parser data from source code
    def from_source(self, inputs_py, display_py):
        self.__csts = {
            "inputs_py": libcst.parse_module(inputs_py),
            "display_py": libcst.parse_module(display_py)
        }

    # Returns a dict holding the sources for the current configuration
    def to_source(self):
        if not self.__csts:
            raise Exception("No data loaded")
        
        self._remove_unused_imports()

        return {
            "inputs_py": self.__csts["inputs_py"].code,
            "display_py": self.__csts["display_py"].code
        }

    # Returns the visitor/handler of the input assigned to the port given
    def input(self, port):
        if not self.__csts:
            raise Exception("No data loaded")
        
        visitor = Input(self, self.__hw_import_path, port)
        self.__csts["inputs_py"].visit(visitor)
        return visitor if visitor.result != None else None
    
    ########################################################################################

    # Update the CSTs from the passed input. Only called internally.
    def update_input(self, input):
        if not self.__csts:
            raise Exception("No data loaded")

        visitor = InputReplacer(input)
        self.__csts["inputs_py"] = self.__csts["inputs_py"].visit(visitor)
        
    # Remove unised imports on all files
    def _remove_unused_imports(self):
        self._remove_unused_import_for_file("inputs_py")
        self._remove_unused_import_for_file("display_py")

    def _remove_unused_import_for_file(self, file):
        wrapper = libcst.metadata.MetadataWrapper(self.__csts[file])
        visitor = RemoveUnusedImportTransformer(wrapper)
        self.__csts[file] = wrapper.module.visit(visitor)
