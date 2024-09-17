import displayio
from adafruit_display_text import label, wrap_text_to_pixels
from adafruit_display_shapes.rect import Rect

from ..Tools import Tools
from ...definitions import Colors
from ...config import Config


# Controller for a generic rectangular label on the user interface.
class DisplayLabel:

    # layout:
    # {
    #     "font": Path to the font, example: "/fonts/H20.pcf"
    #     "maxTextWidth": Maximum text width in pixels (default: 220) optional
    #     "lineSpacing": Line spacing (optional), float (default: 1)
    #     "textColor": Text color (default is auto)
    #     "backColor": Background color (default is none)
    #     "text": Initial text (default is none)
    # }
    def __init__(self, ui, x, y, width, height, layout, id):
        self.ui = ui
        self.layout = layout
        
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)

        self._font = self.ui.font_loader.get(self.layout["font"])

        self._max_text_width = Tools.get_option(self.layout, "maxTextWidth")
        self._line_spacing = Tools.get_option(self.layout, "lineSpacing")
        self._text = Tools.get_option(self.layout, "text", "")
        self._text_color = Tools.get_option(self.layout, "textColor", None)
        self._back_color = Tools.get_option(self.layout, "backColor", None)
        self._initial_text_color = self._text_color
        self.id = id

        self._background_splash_address = -1

        self._add_to_splash()

    # Adds the slot to the splash
    def _add_to_splash(self):
        # Append background, if any
        if self.back_color != None:
            # Remember the index of the background Rect
            self._background_splash_address = len(self.ui.splash)

            self.ui.splash.append(self._create_background(self.back_color))        

        # Append text area
        self._label = label.Label(
            self._font,
            color = self.text_color,
            anchor_point = (0.5, 0.5), 
            anchored_position = (
                int(self.width / 2), 
                int(self.height / 2)
            ),
            line_spacing = self._line_spacing
        )
        self.text = self._text
        self.back_color = self._back_color
        self.text_color = self._text_color
        
        group = displayio.Group(
            scale = 1, 
            x = self.x, 
            y = self.y
        )

        group.append(self._label) 
        
        self._label_splash_address = len(self.ui.splash)
        self.ui.splash.append(group)        

    @property
    def back_color(self):
        return self._back_color

    @back_color.setter
    def back_color(self, color):
        if self._background_splash_address < 0:
            return
        
        if self._back_color == color:
            return

        self._print("Set back color to " + repr(color))

        self._back_color = color
        self.ui.splash[self._background_splash_address] = self._create_background(color)

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
        
        self._print("Set text color to " + repr(color))

        self._text_color = text_color
        self._label.color = text_color

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
        
        self._print("Set text to " + text_out)

        self._text = text_out
        self._label.text = text_out

    # Create background Rect
    def _create_background(self, color):
        return Rect(
            self.x, 
            self.y,
            self.width, 
            self.height, 
            fill = color,
            outline = 0x0, 
            stroke = 1
        )

    # Determines a matching text color to the current background color.
    # Algorithm adapted from https://nemecek.be/blog/172/how-to-calculate-contrast-color-in-python
    def _determine_text_color(self):
        if self.back_color == None:
            return Colors.WHITE
        
        luminance = self._get_luminance(self.back_color)

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
        if Tools.get_option(Config, "debugDisplay") != True:
            return
        
        Tools.print("Label " + self.id + ": " + msg)