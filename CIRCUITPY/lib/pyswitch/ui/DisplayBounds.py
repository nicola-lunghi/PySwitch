
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