from displayio import Group
from ..misc import Tools


# Couples a root element with a splash group
class DisplaySplash:

    def __init__(self, element, font_loader):
        self.font_loader = font_loader

        self.splash = Group()

        self.root = element        
        

########################################################################################################################


# Represents a screen area with dimensions.
class DisplayBounds:
    def __init__(self, x = 0, y = 0, w = 0, h = 0):
        self.x = x
        self.y = y
        self.width = w
        self.height = h 

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.width == other.width and self.height == other.height

    def __repr__(self):
        return repr((self.x, self.y, self.width, self.height))
    
    def clone(self):
        return DisplayBounds(
            self.x,
            self.y,
            self.width,
            self.height
        )

    @property
    def empty(self):
        return self.width == 0 or self.height == 0

    # Returns a copy which is translated
    def translated(self, x, y):
        cl = self.clone()
        cl.translate(x, y)
        return cl

    # Move by
    def translate(self, x, y):
        self.x = self.x + x
        self.y = self.y + y

    # Removes a part of the rectangle and returns it.
    def remove_from_top(self, amount):
        ret = DisplayBounds(
            self.x,
            self.y,
            self.width,
            amount
        )

        self.y = self.y + amount
        self.height = self.height - amount
        
        return ret
    
    # Removes a part of the rectangle and returns it.
    def remove_from_bottom(self, amount):
        ret = DisplayBounds(
            self.x,
            self.y + self.height - amount,
            self.width,
            amount
        )

        self.height = self.height - amount
        
        return ret
    
    # Removes a part of the rectangle and returns it.
    def remove_from_left(self, amount):
        ret = DisplayBounds(
            self.x,
            self.y,
            amount,
            self.height
        )

        self.x = self.x + amount
        self.width = self.width - amount
        
        return ret
    
    # Removes a part of the rectangle and returns it.
    def remove_from_right(self, amount):
        ret = DisplayBounds(
            self.x + self.width - amount,
            self.y,
            amount,
            self.height
        )

        self.width = self.width - amount
        
        return ret

    # Returns a part of the rectangle without modifying it
    def top(self, amount):
        return DisplayBounds(
            self.x,
            self.y,
            self.width,
            amount
        )
    
    # Returns a part of the rectangle without modifying it
    def bottom(self, amount):
        return DisplayBounds(
            self.x,
            self.y + self.height - amount,
            self.width,
            amount
        )
    
    # Returns a part of the rectangle without modifying it
    def left(self, amount):
        return DisplayBounds(
            self.x,
            self.y,
            amount,
            self.height
        )

    # Returns a part of the rectangle without modifying it    
    def right(self, amount):
        return DisplayBounds(
            self.x + self.width - amount,
            self.y,
            amount,
            self.height
        )
    
    # Returns a copy of the rectangle at the given position
    def with_position(self, x, y):
        return DisplayBounds(
            x,
            y,
            self.width,
            self.height
        )


########################################################################################################


# Base class for all display elements
class DisplayElement:

    def __init__(self, bounds = DisplayBounds(), name = "", id = 0):
        self._bounds = bounds.clone()
        self.name = name
        self.id = id
        self._initialized = False
        
    # Adds the element to the splash
    def init(self, ui, appl):
        self._initialized = True

    def initialized(self):
        return self._initialized

    # Search for a display element matching the condition.
    def search(self, position):
        if position["id"] == self.id:
            return self
        return None

    # Returns a list of all contained DisplayElements.
    def contents_flat(self):
        return [self]

    # Returns a clone (changes on the returned object shall not reflect to this instance)
    @property
    def bounds(self):
        return self._bounds.clone()
    
    @bounds.setter
    def bounds(self, bounds):
        if self._initialized:
            raise Exception(repr(self.id) + ": Bounds of Display Elements cannot be changed after init()")
        
        self._bounds = bounds
        self.bounds_changed()

    # Called when the bounds have been changed.
    def bounds_changed(self):
        pass                                       # pragma: no cover

    # Prints some debug info
    def print_debug_info(self, indentation = 0):   # pragma: no cover
        prefix = ""
        for i in range(indentation):
            prefix = prefix + "  "
        
        Tools.print(prefix + self.__class__.__name__ + " " + repr(self.name) + "(" + repr(self.id) + ") at " + repr(self.bounds))


#######################################################################################################################################


# Base class for elements containing other elements
class HierarchicalDisplayElement(DisplayElement):

    def __init__(self, bounds = DisplayBounds(), children = None, name = "", id = 0):
        super().__init__(bounds = bounds, name = name, id = id)
        
        self._children = children if children else []
        
    @property
    def children(self):        
        return self._children

    @property
    def first_child(self):
        if not self._children:
            return None
        
        index = 0
        while not self._children[index] and index < len(self._children):
            index += 1

        return self._children[index]

    @property
    def last_child(self):
        if not self._children:
            return None
        
        index = len(self._children) - 1
        while not self._children[index] and index > 0:
            index -= 1

        return self._children[index]

    # Initialize the elemenmt and all children
    def init(self, ui, appl):
        super().init(ui, appl)

        for child in self._children:
            if child == None:
                continue
            
            if child.initialized():
                continue

            child.init(ui, appl)

    def initialized(self):
        if not super().initialized():
            return False

        for child in self._children:
            if child == None:
                continue
            
            if not child.initialized():
                return False
            
        return True
    
    # Also notify all children that the bounds have been changed
    def bounds_changed(self):
        super().bounds_changed()

        for child in self._children:
            if not child:
                continue

            child.bounds_changed()

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
        if index < 0:
            raise Exception("Invalid set index: " + repr(index))
        
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
            if not child:
                continue
            
            result = child.search(position)
            if result:
                # Child has found something
                return result
            
        return None

    # Returns a list of all contained DisplayElements.
    def contents_flat(self):
        ret = [self]

        for child in self._children:
            if not child:
                continue

            ret += child.contents_flat()

        return ret

    # Prints some debug info
    def print_debug_info(self, indentation = 0):   # pragma: no cover
        super().print_debug_info(indentation)

        for child in self._children:
            child.print_debug_info(indentation + 1)

