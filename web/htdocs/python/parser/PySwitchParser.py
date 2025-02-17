import libcst

from .inputs.Input import Input
from .inputs.InputReplacer import InputReplacer

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
        