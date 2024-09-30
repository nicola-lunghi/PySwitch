import displayio
from adafruit_display_text import label, wrap_text_to_pixels

from .base.HierarchicalDisplayElement import HierarchicalDisplayElement
from .DisplayRectangle import DisplayRectangle
from ..DisplayBounds import DisplayBounds
from ...core.misc.Tools import Tools
from ...definitions import Colors


# Controller for a generic rectangular label on the user interface.
class DisplayLabel(HierarchicalDisplayElement):

    # layout:
    # {
    #     "font": Path to the font, example: "/fonts/H20.pcf"
    #     "maxTextWidth": Maximum text width in pixels (default: 220) optional
    #     "lineSpacing": Line spacing (optional), float (default: 1)
    #     "textColor": Text color (default is auto)
    #     "backColor": Background color (default is none) Can be a tuple also to show a rainbow background
    #     "cornerRadius": Corner radius (optional: default is 0)
    #     "stroke": Ouline stroke (optional)
    #     "text": Initial text (default is none)
    # }
    def __init__(self, bounds = DisplayBounds(), layout = {}, name = "", id = 0):
        super().__init__(bounds, name, id)

        self._font_path = layout["font"]
        self._max_text_width = Tools.get_option(layout, "maxTextWidth")
        self._line_spacing = Tools.get_option(layout, "lineSpacing")
        self._text = Tools.get_option(layout, "text", "")
        self._text_color = Tools.get_option(layout, "textColor", None)
        self._back_color = Tools.get_option(layout, "backColor", None)
        self._corner_radius = Tools.get_option(layout, "cornerRadius", 0)
        self._stroke = Tools.get_option(layout, "stroke", 0)
        self._initial_text_color = self._text_color
        self._layout = layout
        
        self._backgrounds = []    # Array of backgrounds, one for each color. If no back color is passed, 
                                  # it is currently not possible to add backgrounds afterwards.
        self._frame = None        # Frame (only shown when stroke is > 0 and a back color is set)
        self._label = None        # Label for the text

    # Adds the slot to the splash
    def init(self, ui, appl):
        self._font = ui.font_loader.get(self._font_path)

        # Append background, if any
        if self.back_color != None:
            self._backgrounds = self._create_backgrounds()
            self._frame = self._create_frame()    

            if len(self._backgrounds) > 2:
                # Multi backgrounds: Add first and last backgrounds first to enable overlap to show corner radius correctly
                self.add(self._backgrounds[0])
                self.add(self._backgrounds[len(self._backgrounds) - 1])
                for i in range(1, len(self._backgrounds) - 1):
                    self.add(self._backgrounds[i])
            else:                
                for bg in self._backgrounds:
                    self.add(bg)

            if self._frame != None:
                self.add(self._frame)

        # Trigger automatic text color determination
        self.text_color = self._text_color

        # Trigger text wrapping
        self.text = self._text

        # Append text area
        self._label = label.Label(
            self._font,
            anchor_point = (0.5, 0.5), 
            anchored_position = (
                int(self.width / 2), 
                int(self.height / 2)
            ),
            text = self._wrap_text(self._text),
            color = self._text_color,
            line_spacing = self._line_spacing
        )
        
        self._group = displayio.Group(
            scale = 1, 
            x = self.x, 
            y = self.y
        )
        self._group.append(self._label)

        # Adds all backgrounds and the frame to the splash
        super().init(ui, appl)

        # Add label (group) to splash        
        ui.splash.append(self._group)    

    # Updates all dimensions (called by super class)
    def bounds_changed(self):        
        self._update_label_bounds()
        self._update_background_bounds()

    @property
    def back_color(self):
        return self._back_color

    @back_color.setter
    def back_color(self, color):
        if self._back_color == None:
            raise Exception("You can only change the color if an initial color has been passed (not implemented yet)")
        
        if isinstance(color[0], tuple):
            if not isinstance(self._back_color[0], tuple):
                raise Exception("Color type (tuple or single color) cannot be changed")
            
            if len(color) != len(self._back_color):
                raise Exception("Invalid amount of colors: " + repr(color) + " has to have " + repr(len(self._back_color)) + " entries (" + self.name + ")")

        if self._back_color == color:
            return

        if self.debug == True:
            self.print("Set back color to " + repr(color))

        self._back_color = color

        for i in range(len(self._backgrounds)):
            background = self._backgrounds[i]

            if isinstance(color[0], tuple):
                background.color = color[i]
            else:
                background.color = color

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
        
        if self.debug == True:
            self.print("Set text color to " + repr(text_color))

        self._text_color = text_color

        if self._label != None:
            self._label.color = text_color

    @property
    def corner_radius(self):
        return self._corner_radius
    
    @corner_radius.setter
    def corner_radius(self, r):
        if self._corner_radius == r:
            return
        
        self._corner_radius = r

        if self._back_color != None:
            if isinstance(self._back_color[0], tuple):
                self._backgrounds[0].corner_radius = r
                self._backgrounds[len(self._back_color) - 1].corner_radius = r
            else:
                for background in self._backgrounds:
                    background.corner_radius = r

        if self._frame != None:
            self._frame.corner_radius = r

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        if self._text == text:
            return
        
        if self.debug == True:
            self.print("Set text to " + text)

        self._text = text

        if self._label != None:
            self._label.text = self._wrap_text(text)

    def _wrap_text(self, text):
        if self._max_text_width != False:
            # Wrap text if requested
            return "\n".join(
                wrap_text_to_pixels(
                    text, 
                    self._max_text_width,
                    self._font
                )
            )
        else:
            return text

    # Update label dimensions
    def _update_label_bounds(self):
        # Label
        if self._label == None:
            return
        
        self._label.anchored_position = (
            int(self.width / 2), 
            int(self.height / 2)
        )
        self._group.x = self.x
        self._group.y = self.y

    # Update background dimensions if needed
    def _update_background_bounds(self):
        if self._back_color == None:
            return
        
        # Frame
        if self._frame != None:
            self._frame.bounds = self.bounds

        # Backgrounds
        for i in range(len(self._backgrounds)):
            background = self._backgrounds[i]
            bg_bounds = self._get_background_bounds(i)

            if background.bounds != bg_bounds:
                background.bounds = bg_bounds

    # For multicolor, this generates the dimensions for each background
    def _get_background_bounds(self, index):
        if self._back_color == None:
            raise Exception("No background exists to get bounds for")
        
        if not isinstance(self._back_color[0], tuple):
            return self.bounds
        
        bg_height = int(self.height / len(self._back_color))
        overlap_top = 0
        overlap_bottom = 0
        if index == 0:
            overlap_bottom = self._corner_radius
        if index == len(self._back_color) - 1:
            overlap_top = self._corner_radius
        
        return DisplayBounds(
            x = self.x,
            y = self.y + index * bg_height - overlap_top,
            w = self.width,
            h = bg_height + overlap_top + overlap_bottom,
        )

    # Returns new backgrounds list
    def _create_backgrounds(self):
        if isinstance(self._back_color[0], tuple):
            ret = []            
    
            # Create the middle backgrounds without corner radius
            for i in range(len(self._back_color)):
                if i == 0 or i == len(self._back_color) - 1:
                    r = self._corner_radius
                else:
                    r = 0

                ret.append(
                    DisplayRectangle(
                        bounds = self._get_background_bounds(i),
                        color = self._back_color[i],
                        corner_radius = r,
                        name = "Back " + repr(i)
                    )
                )

            return ret
        else:
            # Single background
            return [
                DisplayRectangle(
                    bounds = self.bounds,
                    color = self._back_color,
                    corner_radius = self._corner_radius,
                    name = "Back"
                )
            ]          

    # Creates the frame if a stroke is set
    def _create_frame(self):
        if self._stroke <= 0:
            return None
        
        return DisplayRectangle(
            bounds = self.bounds,
            corner_radius = self._corner_radius,
            stroke = self._stroke,
            outline = Colors.BLACK,
            name = "Frame"
        )

    # Determines a matching text color to the current background color.
    # Algorithm adapted from https://nemecek.be/blog/172/how-to-calculate-contrast-color-in-python
    def _determine_text_color(self):
        if self.back_color == None:
            return Colors.WHITE
        
        if isinstance(self._back_color[0], tuple):
            luminance = 0
            for bg_col in self._back_color:
                bg_luminance = self._get_luminance(bg_col)
                if bg_luminance > luminance:
                    luminance = bg_luminance
        else:
            luminance = self._get_luminance(self.back_color)

        if self.debug == True:
            self.print("Determine text color: luminance " + repr(luminance) + " for back color(s) " + repr(self.back_color))

        if luminance < 140:
            return Colors.WHITE
        else:
            return Colors.BLACK
        
    # Get the luminance of a color, in range [0..255]. 
    def _get_luminance(self, color):
        return color[0] * 0.2126 + color[1] * 0.7151 + color[2] * 0.0721

