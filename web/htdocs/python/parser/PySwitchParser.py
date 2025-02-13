import libcst
# import libcst.matchers as m
# from libcst.display import dump

from .inputs.Input import Input
from .inputs.InputReplacer import InputReplacer

class PySwitchParser:

    # Returns a CST tree for a given source
    def parse(self, source):
        return libcst.parse_module(source)
            
    # Returns unparsed source code for the CST tree passed
    def unparse(self, cst):
        return cst.code
    
    # Returns the visitor of the input assigned to the port given
    def input(self, inputs_cst, hw_import_path, port):
        visitor = Input(hw_import_path, port)
        inputs_cst.visit(visitor)
        return visitor if visitor.result != None else None
    
    # Returns a new CST with the (matching) input replaced with the passed one (instance of Input)
    def replace_input(self, inputs_cst, input):
        visitor = InputReplacer(input)
        return inputs_cst.visit(visitor)
        