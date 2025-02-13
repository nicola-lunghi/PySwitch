import json
import libcst
# import libcst.matchers as m
# from libcst.display import dump

from .inputs.Input import Input

class PySwitchParser:

    # def __init__(self):
    #     self.__inputs = None

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
    
