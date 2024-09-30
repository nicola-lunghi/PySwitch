from adafruit_display_shapes.circle import Circle

from .base.DisplayElement import DisplayElement
from ..DisplayBounds import DisplayBounds

# Circle element.
class DisplayCircle(DisplayElement):

    def __init__(self, bounds = DisplayBounds(), radius = None, name = "", color = None, outline = None, stroke = 0, id = 0):
        super().__init__(bounds, name, id)
        
        self._color = color
        self._outline = outline
        self._stroke = stroke

        if radius != None:
            self.bounds.width = radius * 2
            self.bounds.height = radius * 2

        self._element = None
        self._element_splash_index = -1  
        
        self._ui = None      

    # Adds the background to the splash
    def init(self, ui, appl):
        self._element_splash_index = len(ui.splash)
        self._element = self._create()
                
        ui.splash.append(self._element)

        self._ui = ui

    # Update if changed
    def bounds_changed(self):        
        if self._element == None:
            return
        
        if self._element.x != self.x or self._element.y != self.y or self._element.width != self.width or self._element.height != self.height:
            self._recreate()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        if self._color == color:
            return

        self._color = color

        if self._element != None and self._element.fill != color:
            self._element.fill = color

    @property
    def radius(self):
        return self.width / 2
    
    @radius.setter
    def radius(self, r):
        if self.width / 2 == r:
            return
        
        self.bounds = DisplayBounds(
            self.x, 
            self.y,
            r * 2,
            r * 2
        )

    @property
    def stroke(self):
        return self._stroke
    
    @stroke.setter
    def stroke(self, value):
        if self._stroke == value:
            return
        
        self._stroke = value

        self._element.stroke = value

    @property
    def outline(self):
        return self._outline
    
    @outline.setter
    def outline(self, value):
        if self._outline == value:
            return
        
        self._outline = value

        self._element.outline = value

    # Refresh the background by replacing it (necessary when dimensions have changed only)
    def _recreate(self):
        if self._ui == None:
            return
        
        self._element = self._create()
        self._ui.splash[self._element_splash_index] = self._element

    # Create background Rect
    def _create(self):
        if self.bounds.empty:
            raise Exception("No bounds set for circle " + self.name + "(" + repr(self.id) + "): " + repr(self.bounds))

        r = 0
        if self.width > self.height:
            r = int(self.width / 2)
        else:
            r = int(self.height / 2)

        return Circle(
            x0 = self.x + r, 
            y0 = self.y + r,
            r = r, 
            fill = self._color,
            outline = self._outline, 
            stroke = self._stroke
        )
