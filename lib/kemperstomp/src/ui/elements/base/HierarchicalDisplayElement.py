from .DisplayElement import DisplayElement
from ....misc.Tools import Tools
from ...DisplayBounds import DisplayBounds


# Base class for elements containing other elements
class HierarchicalDisplayElement(DisplayElement):

    def __init__(self, bounds = DisplayBounds(), name = "", id = 0):
        super().__init__(bounds, name, id)
        
        self._children = []        
        
    @property
    def children(self):        
        return self._children

    # Initialize the elemenmt and all children
    def init(self, ui, appl):
        super().init(ui, appl)

        for child in self._children:
            if child == None:
                continue
            
            child.init(ui, appl)

    # Returns the child element at position index
    def child(self, index):
        if index < 0 or index >= len(self._children): 
            raise Exception("Index out of range: " + repr(index))
        return self._children[index]

    # Adds a child to the element. Returns the index of the new element.
    def add(self, child):
        self._children.append(child)
        return len(self._children) - 1

    # Sets an element at the specified index.
    def set(self, element, index):
        while len(self._children) <= index:
            self.add(None)

        self._children[index] = element            

    # Search for the first child matching the conditions. If
    # an "index" value is passed, the child at this position is returned.
    def search(self, position):
        result = super().search(position)
        if result != None:
            # This element matches the ID: Check if an index is also present
            index = Tools.get_option(position, "index", None)

            if index == None:
                # No index: Return this element
                return result
            elif index >= 0 and index < len(self._children):
                # Index: Return the n-th child of this element
                return self.child(index)

        # Also search in children
        for child in self._children:
            if child == None:
                continue
            
            result = child.search(position)
            if result != None:
                # Child has found something
                return result
            
        return None

    # Prints some debug info
    def print_debug_info(self, indentation = 0):
        super().print_debug_info(indentation)

        for child in self._children:
            child.print_debug_info(indentation + 1)

