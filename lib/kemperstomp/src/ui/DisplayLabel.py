import displayio

from adafruit_display_text import label, wrap_text_to_pixels
from adafruit_display_shapes.rect import Rect

from ..Tools import Tools

from ...kemperstomp_def import Colors

# Controller for a generic rectangular label on the user interface.
class DisplayLabel:

    # config:
    # {
    #     "font": Path to the font, example: "/fonts/H20.pcf"
    #     "maxTextWidth": Maximum text width in pixels (default: 220) optional
    #     "lineSpacing": Line spacing (optional), float (default: 1)
    # }
    def __init__(self, ui, x, y, width, height, config, text = "", back_color = None, text_color = None):
        self.ui = ui

        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)

        self.config = config
        self.font = self.ui.font_loader.get(self.config["font"])

        self.max_text_width = Tools.get_option(self.config, "maxTextWidth")
        self.line_spacing = Tools.get_option(self.config, "lineSpacing")

        self.initial_text = text

        self.back_color = back_color
        self.text_color = text_color

        self._add_to_splash()

    # Adds the slot to the splash
    def _add_to_splash(self):
        # Append background, if any
        if self.back_color != None:
            self.background_splash_address = len(self.ui.splash)
            self.ui.splash.append(self._create_background(self.back_color))        

        # Append text area
        self.label = label.Label(
            self.font,
            color = self._get_text_color(),
            anchor_point = (0.5, 0.5), 
            anchored_position = (
                int(self.width / 2), 
                int(self.height / 2)
            ),
            line_spacing = self.line_spacing
        )
        self.set_text(self.initial_text)
        
        group = displayio.Group(
            scale = 1, 
            x = self.x, 
            y = self.y
        )

        group.append(self.label) 
        
        self.label_splash_address = len(self.ui.splash)
        self.ui.splash.append(group)        

    # Sets the background color
    def set_back_color(self, color):
        self.back_color = color
        self.ui.splash[self.background_splash_address] = self._create_background(color)

        # Also set text color again (might have been changed)
        if self.text_color == None:
            self.label.color = self._get_text_color()

    # Sets the text
    def set_text(self, text):
        if self.max_text_width != False:
            # Wrap text if requested
            text_out = "\n".join(
                wrap_text_to_pixels(
                    text, 
                    self.max_text_width,
                    self.font
                )
            )
        else:
            text_out = text

        self.text = text_out
        self.label.text = text_out

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

    # Text color: If none is set, auto-detect according to the background
    def _get_text_color(self):        
        text_color = self.text_color
        if text_color == None:
            text_color = self._determine_text_color()
        return text_color

    # Determines a text color by the current background color.
    # Algorithm adapted from https://nemecek.be/blog/172/how-to-calculate-contrast-color-in-python
    def _determine_text_color(self):
        if self.back_color == None:
            return Colors.WHITE
        
        luminance = self._get_luminance(self.back_color)
        if luminance < 140:
            return Colors.WHITE
        else:
            return Colors.BLACK
        
    # Get the luminance of a color, in range [0..255]. 
    def _get_luminance(self, color):
        return color[0] * 0.2126 + color[1] * 0.7151 + color[2] * 0.0721

