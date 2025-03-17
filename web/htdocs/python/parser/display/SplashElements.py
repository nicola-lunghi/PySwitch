import libcst
from .SplashElement import SplashElement
from ..misc.VisitorsWithStack import VisitorWithStack

class SplashElements(VisitorWithStack):
    def __init__(self, parser):
        super().__init__()
        self.parser = parser

        self.__display_element_level = None
        self.result = []
        
    # Elements of the main input dict
    def visit_Call(self, node):
        if isinstance(node.func, libcst.Name) and node.func.value == "DisplayElement":
            self.__display_element_level = len(self.stack)

    def visit_Arg(self, node):
        if self.__display_element_level and len(self.stack) != self.__display_element_level + 1:
            return True
        
        if node.keyword.value != "children":
            return True

        self.__children = True        
        
    def leave_Arg(self, node):
        self.__children = None
        
    def visit_Element(self, node):
        if not self.__children:
            return False
        
        element = SplashElement(self.parser, node.value)
        self.result.append(element)
        