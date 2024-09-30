from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.roundrect import RoundRect

from .base.DisplayElement import DisplayElement
from ..DisplayBounds import DisplayBounds

# Rectangle element.
class DisplayRectangle(DisplayElement):

    def __init__(self, bounds = DisplayBounds(), name = "", color = None, corner_radius = 0, outline = None, stroke = 0, id = 0):
        super().__init__(bounds, name, id)
        
        self._color = color
        self._corner_radius = corner_radius        
        self._outline = outline
        self._stroke = stroke

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
    def corner_radius(self):
        return self._corner_radius
    
    @corner_radius.setter
    def corner_radius(self, r):
        if self._corner_radius == r:
            return
        
        self._corner_radius = r

        if self._element != None and self._element.r != r:
            self._recreate()

    # Refresh the background by replacing it (necessary when dimensions have changed only)
    def _recreate(self):
        if self._ui == None:
            return
        
        self._element = self._create()
        self._ui.splash[self._element_splash_index] = self._element

    # Create background Rect
    def _create(self):
        if self.bounds.empty:
            raise Exception("No bounds set for rectangle " + self.name + "(" + repr(self.id) + "): " + repr(self.bounds))

        if self._corner_radius <= 0:
            return Rect(
                self.x, 
                self.y,
                self.width, 
                self.height, 
                fill = self._color,
                outline = self._outline, 
                stroke = self._stroke
            )
        else:
            return RoundRect(
                self.x, 
                self.y,
                self.width, 
                self.height, 
                fill = self._color,
                outline = self._outline, 
                stroke = self._stroke,
                r = self._corner_radius
            )
