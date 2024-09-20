import displayio
from adafruit_display_text import label, wrap_text_to_pixels
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.roundrect import RoundRect

from ..Tools import Tools
from ...definitions import Colors


# Controller for a generic rectangular label on the user interface.
class DisplayLabel:

    # layout:
    # {
    #     "font": Path to the font, example: "/fonts/H20.pcf"
    #     "maxTextWidth": Maximum text width in pixels (default: 220) optional
    #     "lineSpacing": Line spacing (optional), float (default: 1)
    #     "textColor": Text color (default is auto)
    #     "backColor": Background color (default is none)
    #     "cornerRadius": Corner radius (optional: default is 0)
    #     "text": Initial text (default is none)
    # }
    def __init__(self, ui, x, y, width, height, layout, id):
        self._ui = ui
        self.layout = layout
        
        self._debug = Tools.get_option(self._ui.config, "debugDisplay")

        self._x = int(x)
        self._y = int(y)
        self._width = int(width)
        self._height = int(height)

        self._font = self._ui.font_loader.get(self.layout["font"])

        self._max_text_width = Tools.get_option(self.layout, "maxTextWidth")
        self._line_spacing = Tools.get_option(self.layout, "lineSpacing")
        self._text = Tools.get_option(self.layout, "text", "")
        self._text_color = Tools.get_option(self.layout, "textColor", None)
        self._back_color = Tools.get_option(self.layout, "backColor", None)
        self._corner_radius = Tools.get_option(self.layout, "cornerRadius", 0)
        self._initial_text_color = self._text_color
        self.id = id

        self._background_splash_address = -1

        self._add_to_splash()    

    # Adds the slot to the splash
    def _add_to_splash(self):
        # Append background, if any
        if self.back_color != None:
            # Remember the index of the background Rect
            self._background_splash_address = len(self._ui.splash)

            self._ui.splash.append(self._create_background(self.back_color))        

        # Append text area
        self._label = label.Label(
            self._font,
            #color = self.text_color,
            anchor_point = (0.5, 0.5), 
            anchored_position = (
                int(self._width / 2), 
                int(self._height / 2)
            ),
            line_spacing = self._line_spacing
        )
        
        self.text = self._text
        self.back_color = self._back_color
        self.text_color = self._text_color
        
        self._group = displayio.Group(
            scale = 1, 
            x = self._x, 
            y = self._y
        )

        self._group.append(self._label) 
        
        self._label_splash_address = len(self._ui.splash)
        self._ui.splash.append(self._group)    

    # Sets all dimensions at once: (x, y, w, h)
    @property
    def dimensions(self):
        return (self.x, self.y, self.width, self.height)
    
    @dimensions.setter
    def dimensions(self, dimensions):
        self._x = dimensions[0]
        self._y = dimensions[1]
        self._width = dimensions[2]
        self._height = dimensions[3]

        self._label.anchored_position = (
            int(self._width / 2), 
            int(self._height / 2)
        )
        self._group.x = self._x
        self._group.y = self._y

        self._update_background()

    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, value):
        if self._x == value:
            return
        
        self._x = value        

        self._group.x = value
        self._update_background()

    @property
    def y(self):
        return self._y
    
    @x.setter
    def y(self, value):
        if self._y == value:
            return
        
        self._y = value        

        self._group.y = value
        self._update_background()

    @property
    def width(self):
        return self._width
    
    @x.setter
    def width(self, value):
        if self._width == value:
            return
        
        self._width = value        

        self._label.anchored_position = (
            int(self._width / 2), 
            int(self._height / 2)
        )
        self._update_background()

    @property
    def height(self):
        return self._height
    
    @x.setter
    def height(self, value):
        if self._height == value:
            return
        
        self._height = value        

        self._label.anchored_position = (
            int(self._width / 2), 
            int(self._height / 2)
        )
        self._update_background()    

    @property
    def back_color(self):
        return self._back_color

    @back_color.setter
    def back_color(self, color):
        if self._background_splash_address < 0:
            return
        
        if self._back_color == color:
            return

        if self._debug == True:
            self._print("Set back color to " + repr(color))

        self._back_color = color
        self._update_background()

        # Update text color, too (might change when no initial color has been set)
        self.text_color = self._initial_text_color

    @property
    def text_color(self):
        return self._text_color

    @text_color.setter
    def text_color(self, color):
        text_color = color        
        if text_color == None:
            text_color = self._determine_text_color()

        if self._text_color == text_color:
            return
        
        if self._debug == True:
            self._print("Set text color to " + repr(text_color))

        self._text_color = text_color
        self._label.color = text_color

    @property
    def corner_radius(self):
        return self._corner_radius
    
    @corner_radius.setter
    def corner_radius(self, r):
        if self._corner_radius == r:
            return
        
        self._corner_radius = r

        self._update_background()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        if self._max_text_width != False:
            # Wrap text if requested
            text_out = "\n".join(
                wrap_text_to_pixels(
                    text, 
                    self._max_text_width,
                    self._font
                )
            )
        else:
            text_out = text

        if self._text == text_out:
            return
        
        if self._debug == True:
            self._print("Set text to " + text_out)

        self._text = text_out
        self._label.text = text_out

    # Updates the display to match the back color
    def _update_background(self):
        if self._background_splash_address < 0:
            return
        
        self._ui.splash[self._background_splash_address] = self._create_background(self._back_color)

    # Create background Rect
    def _create_background(self, color):
        if self._corner_radius <= 0:
            return Rect(
                self._x, 
                self._y,
                self._width, 
                self._height, 
                fill = color,
                outline = 0x0, 
                stroke = 1
            )
        else:
            return RoundRect(
                self._x, 
                self._y,
                self._width, 
                self._height, 
                fill = color,
                outline = 0x0, 
                stroke = 1,
                r = self._corner_radius
            )

    # Determines a matching text color to the current background color.
    # Algorithm adapted from https://nemecek.be/blog/172/how-to-calculate-contrast-color-in-python
    def _determine_text_color(self):
        if self.back_color == None:
            return Colors.WHITE
        
        luminance = self._get_luminance(self.back_color)

        if self._debug == True:
            self._print("Determine text color: luminance " + repr(luminance) + " for back color " + repr(self.back_color))

        if luminance < 140:
            return Colors.WHITE
        else:
            return Colors.BLACK
        
    # Get the luminance of a color, in range [0..255]. 
    def _get_luminance(self, color):
        return color[0] * 0.2126 + color[1] * 0.7151 + color[2] * 0.0721

    # Debug console output
    def _print(self, msg):
        Tools.print("Label " + self.id + ": " + msg)