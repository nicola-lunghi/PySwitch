import displayio
from adafruit_display_text import label, wrap_text_to_pixels

from .base.HierarchicalDisplayElement import HierarchicalDisplayElement
from .DisplayRectangle import DisplayRectangle
from ..DisplayBounds import DisplayBounds
from ...core.misc.Tools import Tools
from ...definitions import Colors,
from ...core.controller.conditions.Condition import Condition, ConditionListener


# Data class for layouts
class DisplayLabelLayout:

    # layout:
    #  {
    #     "font": Path to the font, example: "/fonts/H20.pcf"
    #     "maxTextWidth": Maximum text width in pixels (default: 220) optional
    #     "lineSpacing": Line spacing (optional), float (default: 1)
    #     "textColor": Text color (default is auto)
    #     "backColor": Background color (default is none) Can be a tuple also to show a rainbow background
    #     "cornerRadius": Corner radius (optional: default is 0)
    #     "stroke": Ouline stroke (optional)
    #     "text": Initial text (default is none)
    # }
    def __init__(self, layout = {}):
        self.font_path = Tools.get_option(layout, "font", None)
        self.max_text_width = Tools.get_option(layout, "maxTextWidth")
        self.line_spacing = Tools.get_option(layout, "lineSpacing")
        self.text = Tools.get_option(layout, "text", "")
        self.text_color = Tools.get_option(layout, "textColor", None)
        self.back_color = Tools.get_option(layout, "backColor", None)
        self.corner_radius = Tools.get_option(layout, "cornerRadius", 0)
        self.stroke = Tools.get_option(layout, "stroke", 0)        


######################################################################################################################################


# Controller for a generic rectangular label on the user interface.
class DisplayLabel(HierarchicalDisplayElement, ConditionListener):

    # layout can also be a Condition!
    def __init__(self, bounds = DisplayBounds(), layout = {}, name = "", id = 0):
        super().__init__(bounds, name, id)

        self._layout_def = layout
        self._layout = self._parse_layout()

        self._initial_text_color = self._layout.text_color        

        self._conditions = []

        self._backgrounds = []    # Array of backgrounds, one for each color. If no back color is passed, 
                                  # it is currently not possible to add backgrounds afterwards.
        self._frame = None        # Frame (only shown when stroke is > 0 and a back color is set)
        self._label = None        # Label for the text
        self._ui = None    

    # Adds the slot to the splash
    def init(self, ui, appl):
        self._ui = ui

        for c in self._conditions:
            appl.register_condition(c)

        self._update_font()

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
        self.text_color = self.layout.text_color

        # Trigger text wrapping
        self.text = self.layout.text

        # Append text area
        self._label = label.Label(
            self._font,
            anchor_point = (0.5, 0.5), 
            anchored_position = (
                int(self.width / 2), 
                int(self.height / 2)
            ),
            text = self._wrap_text(self.layout.text),
            color = self.layout.text_color,
            line_spacing = self.layout.line_spacing
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

    # Parse layout (may contain conditions), and returns the default active layout
    def _parse_layout(self):
        result = Condition.parse(
            subject = self._layout_def,
            listener = self,
            factory = self,
            allow_lists = False
        )

        if len(result.objects) == 0:
            return None

        if len(result.objects) > 1:
            raise Exception("INTERNAL ERROR: Non-list condition returned multiple items")

        self._conditions = result.conditions

        return result.objects[0]
    
    # Factory for actions, used by Condition.parse(): data is the customer data in the condition configs, 
    # enabled signals if the condition branch is active by default (assuming that all conditions are true 
    # by default). Can return a model instance or something else which will be collected in the Condition 
    # models, so the listeners can access them later (optional).
    def get_condition_instance(self, data, enabled):
        if enabled != True:
            return None
        return data
    
    # Called on condition changes. The yes value will be True or False.
    def condition_changed(self, condition, bool_value):
        if bool_value == True:
            self.layout = DisplayLabelLayout(condition.model.yes)
        else:
            self.layout = DisplayLabelLayout(condition.model.no)

    # Update font according to layout
    def _update_font(self):
        self._font = self._ui.font_loader.get(self.layout.font_path)

    # Updates all dimensions (called by super class)
    def bounds_changed(self):        
        self._update_label_bounds()
        self._update_background_bounds()

    @property
    def layout(self):
        return self._layout
    
    @layout.setter
    def layout(self, layout):
        old = self._layout
        self._layout = layout
                
        # Changes to the label
        if self._label != None:
            # Font changed?
            if old.font_path != self._layout.font_path:
                self._update_font()
                self._label.font = self._font

            # Text or wrapping changed?
            if old.text != self._layout.text or old.max_text_width != self._layout.max_text_width:
                self._label.text = self._wrap_text(self._layout.text)

            # Line spacing changed?
            if old.line_spacing != self._layout.line_spacing:
                self._label.line_spacing = self._layout.line_spacing

            # Text color changed?
            if old.text_color != self._layout.text_color:
                self._label.color = self._layout.text_color
                self._initial_text_color = self._layout.text_color

        # Changes to the backgrounds
        if self._layout.back_color != None:
            if old.back_color == None:
                raise Exception("You can only change the color if an initial color has been passed (not implemented yet)")
        
            # Back color changed?
            if old.back_color != self._layout.back_color:
                for i in range(len(self._backgrounds)):
                    background = self._backgrounds[i]

                    if isinstance(self._layout.back_color[0], tuple):
                        background.color = self._layout.back_color[i]
                    else:
                        background.color = self._layout.back_color

                # Update text color, too (might change when no initial color has been set)
                self.text_color = self._initial_text_color

            # Corner radius changed?
            if old.corner_radius != self._layout.corner_radius:
                if isinstance(self._layout.back_color[0], tuple):
                    self._backgrounds[0].corner_radius = self._layout.corner_radius
                    self._backgrounds[len(self._layout.back_color) - 1].corner_radius = self._layout.corner_radius
                else:
                    for background in self._backgrounds:
                        background.corner_radius = self._layout.corner_radius

        # Stroke changed?
        if old.stroke != self._layout.stroke:
            if self._layout.stroke > 0:
                if self._frame == None:
                    raise Exception("Cannot switch frame <> noframe (yet)")
                
                self._frame.stroke = self._layout.stroke
            else:
                if self._frame != None:
                    raise Exception("Cannot switch frame <> noframe (yet)")

    @property
    def back_color(self):
        return self.layout.back_color

    @back_color.setter
    def back_color(self, color):
        if self.layout.back_color == None:
            raise Exception("You can only change the color if an initial color has been passed (not implemented yet)")
        
        if isinstance(color[0], tuple):
            if not isinstance(self.layout.back_color[0], tuple):
                raise Exception("Color type (tuple or single color) cannot be changed")
            
            if len(color) != len(self.layout.back_color):
                raise Exception("Invalid amount of colors: " + repr(color) + " has to have " + repr(len(self.layout.back_color)) + " entries (" + self.name + ")")

        if self.layout.back_color == color:
            return

        if self.debug == True:
            self.print("Set back color to " + repr(color))

        self.layout.back_color = color

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
        return self.layout.text_color

    @text_color.setter
    def text_color(self, color):
        text_color = color        
        if text_color == None:
            text_color = self._determine_text_color()

        if self.layout.text_color == text_color:
            return
        
        if self.debug == True:
            self.print("Set text color to " + repr(text_color))

        self.layout.text_color = text_color

        if self._label != None:
            self._label.color = text_color

    @property
    def corner_radius(self):
        return self.layout.corner_radius
    
    @corner_radius.setter
    def corner_radius(self, r):
        if self.layout.corner_radius == r:
            return
        
        self.layout.corner_radius = r

        if self.layout.back_color != None:
            if isinstance(self.layout.back_color[0], tuple):
                self._backgrounds[0].corner_radius = r
                self._backgrounds[len(self.layout.back_color) - 1].corner_radius = r
            else:
                for background in self._backgrounds:
                    background.corner_radius = r

        if self._frame != None:
            self._frame.corner_radius = r

    @property
    def text(self):
        return self.layout.text

    @text.setter
    def text(self, text):
        if self.layout.text == text:
            return
        
        if self.debug == True:
            self.print("Set text to " + text)

        self.layout.text = text

        if self._label != None:
            self._label.text = self._wrap_text(text)

    def _wrap_text(self, text):
        if self.layout.max_text_width != False:
            # Wrap text if requested
            return "\n".join(
                wrap_text_to_pixels(
                    text, 
                    self.layout.max_text_width,
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
        if self.layout == None or self.layout.back_color == None:
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
        if self.layout.back_color == None:
            raise Exception("No background exists to get bounds for")
        
        if not isinstance(self.layout.back_color[0], tuple):
            return self.bounds
        
        bg_height = int(self.height / len(self.layout.back_color))
        overlap_top = 0
        overlap_bottom = 0
        if index == 0:
            overlap_bottom = self.layout.corner_radius
        if index == len(self.layout.back_color) - 1:
            overlap_top = self.layout.corner_radius
        
        return DisplayBounds(
            x = self.x,
            y = self.y + index * bg_height - overlap_top,
            w = self.width,
            h = bg_height + overlap_top + overlap_bottom,
        )

    # Returns new backgrounds list
    def _create_backgrounds(self):
        if isinstance(self.layout.back_color[0], tuple):
            ret = []            
    
            # Create the middle backgrounds without corner radius
            for i in range(len(self.layout.back_color)):
                if i == 0 or i == len(self.layout.back_color) - 1:
                    r = self.layout.corner_radius
                else:
                    r = 0

                ret.append(
                    DisplayRectangle(
                        bounds = self._get_background_bounds(i),
                        color = self.layout.back_color[i],
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
                    color = self.layout.back_color,
                    corner_radius = self.layout.corner_radius,
                    name = "Back"
                )
            ]          

    # Creates the frame if a stroke is set
    def _create_frame(self):
        if self.layout.stroke <= 0:
            return None
        
        return DisplayRectangle(
            bounds = self.bounds,
            corner_radius = self.layout.corner_radius,
            stroke = self.layout.stroke,
            outline = Colors.BLACK,
            name = "Frame"
        )

    # Determines a matching text color to the current background color.
    # Algorithm adapted from https://nemecek.be/blog/172/how-to-calculate-contrast-color-in-python
    def _determine_text_color(self):
        if self.back_color == None:
            return Colors.WHITE
        
        if isinstance(self.layout.back_color[0], tuple):
            luminance = 0
            for bg_col in self.layout.back_color:
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

