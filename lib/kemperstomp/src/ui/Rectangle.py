# Used for layouting.
class Rectangle:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h

    # Removes a part of the rectangle and returns it.
    def remove_from_top(self, amount):
        ret = Rectangle(
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
        ret = Rectangle(
            self.x,
            self.y + self.height - amount,
            self.width,
            amount
        )

        self.height = self.height - amount
        
        return ret
    
    # Removes a part of the rectangle and returns it.
    def remove_from_left(self, amount):
        ret = Rectangle(
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
        ret = Rectangle(
            self.x + self.width - amount,
            self.y,
            amount,
            self.height
        )

        self.width = self.width - amount
        
        return ret

    # Returns a part of the rectangle without modifying it
    def top(self, amount):
        return Rectangle(
            self.x,
            self.y,
            self.width,
            amount
        )
    
    # Returns a part of the rectangle without modifying it
    def bottom(self, amount):
        return Rectangle(
            self.x,
            self.y + self.height - amount,
            self.width,
            amount
        )
    
    # Returns a part of the rectangle without modifying it
    def left(self, amount):
        return Rectangle(
            self.x,
            self.y,
            amount,
            self.height
        )

    # Returns a part of the rectangle without modifying it    
    def right(self, amount):
        return Rectangle(
            self.x + self.width - amount,
            self.y,
            amount,
            self.height
        )
    
    # Returns a copy of the rectangle at the given position
    def with_position(self, x, y):
        return Rectangle(
            x,
            y,
            self.width,
            self.height
        )