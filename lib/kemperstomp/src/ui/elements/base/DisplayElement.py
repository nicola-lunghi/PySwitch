from ....misc.Tools import Tools
from ...DisplayBounds import DisplayBounds

# Base class for all display elements
class DisplayElement:

    def __init__(self, bounds = DisplayBounds(), name = "", id = 0):
        self._bounds = bounds.clone()
        self.name = name
        self.id = id
        self._initialized = False
        
        self.debug = False

    # Adds the element to the splash
    def init(self, ui, appl):
        self._initialized = True
        self.bounds_changed()

    # Called after the bounds have been changed
    def bounds_changed(self):
        pass    

    # Search for a display element matching the condition.
    def search(self, position):
        if position["id"] == self.id:
            return self
        return None

    @property
    def initialized(self):
        return self._initialized

    # Returns a clone (changes on the returned object shall not reflect to this instance)
    @property
    def bounds(self):
        return DisplayBounds(
            self._bounds.x,
            self._bounds.y,
            self._bounds.width,
            self._bounds.height,
        )
    
    # Sets all dimensions at once: (x, y, w, h)
    @bounds.setter
    def bounds(self, bounds):
        if self._bounds == bounds:
            return
        
        self._bounds = bounds
        
        self.bounds_changed()

    @property
    def x(self):
        return self._bounds.x
    
    @x.setter
    def x(self, value):
        if self._bounds.x == value:
            return
        
        self._bounds.x = value        

        self.bounds_changed()

    @property
    def y(self):
        return self._bounds.y
    
    @y.setter
    def y(self, value):
        if self._bounds.y == value:
            return
        
        self._bounds.y = value        

        self.bounds_changed()

    @property
    def width(self):
        return self._bounds.width
    
    @width.setter
    def width(self, value):
        if self._bounds.width == value:
            return
        
        self._bounds.width = value        

        self.bounds_changed()

    @property
    def height(self):
        return self._bounds.height
    
    @height.setter
    def height(self, value):
        if self._bounds.height == value:
            return
        
        self._bounds.height = value        

        self.bounds_changed()

    # Debug console output
    def print(self, msg):
        Tools.print(self.__class__.__name__ + " " + self.name + ": " + msg)

    # Prints some debug info
    def print_debug_info(self, indentation = 0):
        prefix = ""
        for i in range(indentation):
            prefix = prefix + "  "
        
        Tools.print(prefix + self.__class__.__name__ + " " + repr(self.name) + "(" + repr(self.id) + ") at " + repr(self.bounds))

