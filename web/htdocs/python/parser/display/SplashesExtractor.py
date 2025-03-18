from ..misc.CodeExtractor import CodeExtractor

class SplashesExtractor(CodeExtractor):
    
    def __init__(self, parser, cst):
        super().__init__(cst)
        self.parser = parser

    # Can be redefined to define unnamed parameters for specific types. If this
    # returns [], only keyword arguments are allowed or an Exception will be raised.
    def get_arg_names(self, type_name):
        if type_name == "DisplayBounds":
            return ["x", "y", "w", "h"]
        
    # Can be redefined to add/manipulate data for Call output nodes
    def postprocess_call(self, call_data):
        call_data["client"] = self.parser.determine_client(call_data["name"], cst = self.cst)