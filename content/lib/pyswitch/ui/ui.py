from displayio import Group


# Represents a screen area with dimensions.
class DisplayBounds:
    def __init__(self, x = 0, y = 0, w = 0, h = 0):
        self.x = int(x)
        self.y = int(y)
        self.width = int(w)
        self.height = int(h)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.width == other.width and self.height == other.height

    def clone(self):
        return DisplayBounds(
            self.x,
            self.y,
            self.width,
            self.height
        )

    # Returns a copy which is translated
    def translated(self, x, y):
        cl = self.clone()
        cl.translate(int(x), int(y))
        return cl

    # Move by
    def translate(self, x, y):
        self.x = self.x + int(x)
        self.y = self.y + int(y)

    # Removes a part of the rectangle and returns it.
    def remove_from_top(self, amount):
        ret = DisplayBounds(
            self.x,
            self.y,
            self.width,
            int(amount)
        )

        self.y = self.y + int(amount)
        self.height = self.height - int(amount)
        
        return ret
    
    # Removes a part of the rectangle and returns it.
    def remove_from_bottom(self, amount):
        ret = DisplayBounds(
            self.x,
            self.y + self.height - int(amount),
            self.width,
            int(amount)
        )

        self.height = self.height - int(amount)
        
        return ret
    
    # Removes a part of the rectangle and returns it.
    def remove_from_left(self, amount):
        ret = DisplayBounds(
            self.x,
            self.y,
            int(amount),
            self.height
        )

        self.x = self.x + int(amount)
        self.width = self.width - int(amount)
        
        return ret
    
    # Removes a part of the rectangle and returns it.
    def remove_from_right(self, amount):
        ret = DisplayBounds(
            self.x + self.width - int(amount),
            self.y,
            int(amount),
            self.height
        )

        self.width = self.width - int(amount)
        
        return ret

    # Returns a part of the rectangle without modifying it
    def top(self, amount):
        return DisplayBounds(
            self.x,
            self.y,
            self.width,
            int(amount)
        )
    
    # Returns a part of the rectangle without modifying it
    def bottom(self, amount):
        return DisplayBounds(
            self.x,
            self.y + self.height - int(amount),
            self.width,
            int(amount)
        )
    
    # Returns a part of the rectangle without modifying it
    def left(self, amount):
        return DisplayBounds(
            self.x,
            self.y,
            int(amount),
            self.height
        )

    # Returns a part of the rectangle without modifying it    
    def right(self, amount):
        return DisplayBounds(
            self.x + self.width - int(amount),
            self.y,
            int(amount),
            self.height
        )
    
    # Returns a copy of the rectangle at the given position
    def with_position(self, x, y):
        return DisplayBounds(
            int(x),
            int(y),
            self.width,
            self.height
        )


########################################################################################################


# Base class for all display elements
class DisplayElement:

    def __init__(self, bounds = DisplayBounds(), name = "", id = 0):
        self.__bounds = bounds.clone()
        self.name = name
        self.id = id
        self.splash = None

        self.__initialized = False

    # Adds the element to the splash
    def init(self, ui, appl):
        self.__initialized = True
        
    # Makes this element the splash holder which is passed as ui to init() later
    def make_splash(self, font_loader):
        if self.splash:
            return      
        
        self.font_loader = font_loader
        self.splash = Group()

    def initialized(self):
        return self.__initialized

    # Returns a list of all contained DisplayElements.
    def contents_flat(self):
        return [self]

    # Returns a clone (changes on the returned object shall not reflect to this instance)
    @property
    def bounds(self):
        return self.__bounds.clone()
    
    @bounds.setter
    def bounds(self, bounds):
        if self.__initialized:
            raise Exception(repr(self.id) + ": Bounds of Display Elements cannot be changed after init()")
        
        self.__bounds = bounds
        self.bounds_changed()

    # Called when the bounds have been changed.
    def bounds_changed(self):
        pass                                       # pragma: no cover

    # Prints some debug info
    #def print_debug_info(self, indentation = 0):   # pragma: no cover
    #    prefix = ""
    #    for i in range(indentation):
    #        prefix = prefix + "  "
    #    
    #    do_print(prefix + self.__class__.__name__ + " " + repr(self.name) + "(" + repr(self.id) + ") at " + repr(self.bounds))


#######################################################################################################################################


# Base class for elements containing other elements
class HierarchicalDisplayElement(DisplayElement):

    def __init__(self, bounds = DisplayBounds(), children = None, name = "", id = 0):
        super().__init__(bounds = bounds, name = name, id = id)
        
        self.__children = children if children else []
        
    @property
    def children(self):        
        return self.__children

    # Initialize the element and all children
    def init(self, ui, appl):
        super().init(ui, appl)

        for child in self.__children:
            if child == None:
                continue
            
            if child.initialized():
                continue

            child.init(ui, appl)

    # Returns if the element is initialized already
    def initialized(self):
        if not super().initialized():
            return False

        for child in self.__children:
            if child == None:
                continue
            
            if not child.initialized():
                return False
            
        return True
    
    # Also notify all children that the bounds have been changed
    def bounds_changed(self):
        super().bounds_changed()

        for child in self.__children:
            if not child:
                continue

            child.bounds_changed()

    # Adds a child to the element. 
    def add(self, child):
        self.__children.append(child)

    # Returns a list of all contained DisplayElements.
    def contents_flat(self):
        ret = [self]

        for child in self.__children:
            if not child:
                continue

            ret += child.contents_flat()

        return ret

    # Prints some debug info
    #def print_debug_info(self, indentation = 0):   # pragma: no cover
    #    super().print_debug_info(indentation)
    #
    #    for child in self.__children:
    #        if not child:
    #            continue
    #
    #        child.print_debug_info(indentation + 1)

