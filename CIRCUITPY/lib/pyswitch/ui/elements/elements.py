from ...misc import Tools, Updateable, Colors

from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_text import label, wrap_text_to_pixels
from displayio import Group

from .DisplayElement import DisplayElement, HierarchicalDisplayElement, DisplayBounds

from ...controller.ConditionTree import ConditionTree, ConditionTreeEntryReplacer, ConditionListener
from ...controller.Client import ClientRequestListener
from ...controller.measurements import RuntimeMeasurementListener, RuntimeMeasurement


# Base for display shapes
class DisplayShape(DisplayElement):
    def __init__(self, bounds = DisplayBounds(), corner_radius = 0, radius = None, name = "", color = None, outline = None, stroke = 0, id = 0):
        super().__init__(bounds, name, id)
        
        self._color = color
        self._outline = outline
        self._stroke = stroke
        self._corner_radius = corner_radius        

        if radius != None:
            self.bounds.width = radius * 2
            self.bounds.height = radius * 2

        self.element = None
        self._element_splash_index = -1  
        
        self._ui = None

    # Adds the background to the splash
    def init(self, ui, appl):
        self._element_splash_index = len(ui.splash)
        self.element = self.create()
                
        ui.splash.append(self.element)

        self._ui = ui

    # Create the element
    def create(self):
        pass

    # Update if changed
    def bounds_changed(self):        
        if not self.element:
            return
        
        if self.element.x != self.x or self.element.y != self.y or self.element.width != self.width or self.element.height != self.height:
            self.element = self.create()
            self._ui.splash[self._element_splash_index] = self.element
        
    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        if self._color == color:
            return

        self._color = color

        if self.element and self.element.fill != color:
            self.element.fill = color

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

        self.element.stroke = value

    @property
    def outline(self):
        return self._outline
    
    @outline.setter
    def outline(self, value):
        if self._outline == value:
            return
        
        self._outline = value

        self.element.outline = value

    @property
    def corner_radius(self):
        return self._corner_radius
    
    @corner_radius.setter
    def corner_radius(self, r):
        if self._corner_radius == r:
            return
        
        self._corner_radius = r

        if self._element and self._element.r != r:
            self._recreate()


###########################################################################################################################


# Circle element.
class DisplayCircle(DisplayShape):

    def __init__(self, bounds = DisplayBounds(), radius = None, name = "", color = None, outline = None, stroke = 0, id = 0):
        super().__init__(bounds, 0, radius, name, color, outline, stroke, id)
        
    # Create background Rect
    def create(self):
        r = int(self.width / 2) if self.width > self.height else int(self.height / 2)
        return Circle(
            x0 = self.x + r, 
            y0 = self.y + r,
            r = r, 
            fill = self._color,
            outline = self._outline, 
            stroke = self._stroke
        )


###########################################################################################################################


# Rectangle element.
class DisplayRectangle(DisplayShape):

    def __init__(self, bounds = DisplayBounds(), name = "", color = None, corner_radius = 0, outline = None, stroke = 0, id = 0):
        super().__init__(bounds, corner_radius, None, name, color, outline, stroke, id)
        
    # Create background Rect
    def create(self):
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


###########################################################################################################################


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
        self.line_spacing = Tools.get_option(layout, "lineSpacing", 1)
        self.text = Tools.get_option(layout, "text", "")
        self.text_color = Tools.get_option(layout, "textColor", None)
        self.back_color = Tools.get_option(layout, "backColor", None)
        self.corner_radius = Tools.get_option(layout, "cornerRadius", 0)
        self.stroke = Tools.get_option(layout, "stroke", 0)        

    # Check mandatory fields
    def check(self, label_id):
        if not self.font_path:
            raise Exception("No font specified for DisplayLabel " + repr(label_id))


######################################################################################################################################


# Controller for a generic rectangular label on the user interface.
class DisplayLabel(HierarchicalDisplayElement, ConditionListener, ConditionTreeEntryReplacer):

    # Line feed used for display
    LINE_FEED = "\n"

    # layout can also be a Condition!
    def __init__(self, layout, bounds = DisplayBounds(), name = "", id = 0):
        super().__init__(bounds, name, id)

        self._layout_tree = ConditionTree(
            subject = layout,
            listener = self,
            replacer = self,
            allow_lists = False
        )

        self._layout = self._layout_tree.value

        self._initial_text_color = self._layout.text_color        

        self._backgrounds = []    # Array of backgrounds, one for each color. If no back color is passed, 
                                  # it is currently not possible to add backgrounds afterwards.
        self._frame = None        # Frame (only shown when stroke is > 0 and a back color is set)
        self._label = None        # Label for the text
        self._ui = None    

    # Adds the slot to the splash
    def init(self, ui, appl):
        self._ui = ui
        self._layout_tree.init(appl)

        self._update_font()

        # Append background, if any
        if self.back_color:
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
        
        self._group = Group(
            scale = 1, 
            x = self.x, 
            y = self.y
        )
        self._group.append(self._label)

        # Adds all backgrounds and the frame to the splash
        super().init(ui, appl)

        # Add label (group) to splash        
        ui.splash.append(self._group)    

    # Called on condition changes. The yes value will be True or False.
    def condition_changed(self, condition):
        self.layout = self._layout_tree.value

    # Replace layout entries in the layout tree
    def replace(self, entry):
        l = DisplayLabelLayout(entry)
        l.check(self.id)
        return l
        
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
        if self._label:
            # Font changed?
            if old.font_path != self._layout.font_path:
                self._update_font()
                self._label.font = self._font

            # Text or wrapping changed?
            if old.text != self._layout.text or old.max_text_width != self._layout.max_text_width:
                self._layout.text = old.text                              # Keep text!
                self._label.text = self._wrap_text(self._layout.text)

            # Line spacing changed?
            if old.line_spacing != self._layout.line_spacing:
                self._label.line_spacing = self._layout.line_spacing

            # Text color changed?
            if old.text_color != self._layout.text_color:
                self._label.color = self._layout.text_color
                self._initial_text_color = self._layout.text_color

        # Changes to the backgrounds
        if self._layout.back_color:
            if not old.back_color:
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
                if not self._frame:
                    raise Exception("Cannot switch frame usage (yet). Please use stroke in all possible layouts or not at all.")
                
                self._frame.stroke = self._layout.stroke
            else:
                if self._frame:
                    raise Exception("Cannot switch frame usage (yet). Please use stroke in all possible layouts or not at all.")

    @property
    def back_color(self):
        return self.layout.back_color

    @back_color.setter
    def back_color(self, color):
        if not self.layout.back_color:
            raise Exception("You can only change the background color if an initial background color has been passed (not implemented yet)")
        
        if isinstance(color[0], tuple):
            if not isinstance(self.layout.back_color[0], tuple):
                raise Exception(repr(self.id) + ": Color type (tuple or single color) cannot be changed: " + repr(color))
            
            if len(color) != len(self.layout.back_color):
                raise Exception("Invalid amount of colors: " + repr(color) + " has to have " + repr(len(self.layout.back_color)) + " entries (" + self.name + ")")

        if self.layout.back_color == color:
            return

        if self.debug:
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
        if not text_color:
            text_color = self._determine_text_color()

        if self.layout.text_color == text_color:
            return
        
        if self.debug:
            self.print("Set text color to " + repr(text_color))

        self.layout.text_color = text_color

        if self._label:
            self._label.color = text_color

    @property
    def corner_radius(self):
        return self.layout.corner_radius
    
    @corner_radius.setter
    def corner_radius(self, r):
        if self.layout.corner_radius == r:
            return
        
        self.layout.corner_radius = r

        if self.layout.back_color:
            if isinstance(self.layout.back_color[0], tuple):
                self._backgrounds[0].corner_radius = r
                self._backgrounds[len(self.layout.back_color) - 1].corner_radius = r
            else:
                for background in self._backgrounds:
                    background.corner_radius = r

        if self._frame:
            self._frame.corner_radius = r

    @property
    def text(self):
        return self.layout.text

    @text.setter
    def text(self, text):
        if self.layout.text == text:
            return
        
        if self.debug:
            self.print("Set text to " + text)

        self.layout.text = text

        if self._label:
            self._label.text = self._wrap_text(text)

    def _wrap_text(self, text):
        if self.layout.max_text_width != False:
            # Wrap text if requested
            return DisplayLabel.LINE_FEED.join(
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
        if not self._label:
            return
        
        self._label.anchored_position = (
            int(self.width / 2), 
            int(self.height / 2)
        )
        self._group.x = self.x
        self._group.y = self.y

    # Update background dimensions if needed
    def _update_background_bounds(self):
        if not self.layout or not self.layout.back_color:
            return
        
        # Frame
        if self._frame:
            self._frame.bounds = self.bounds

        # Backgrounds
        for i in range(len(self._backgrounds)):
            background = self._backgrounds[i]
            bg_bounds = self._get_background_bounds(i)

            if background.bounds != bg_bounds:
                background.bounds = bg_bounds

    # For multicolor, this generates the dimensions for each background
    def _get_background_bounds(self, index):
        if not self.layout.back_color:
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
        if not self.back_color:
            return Colors.WHITE
        
        if isinstance(self.layout.back_color[0], tuple):
            luminance = 0
            for bg_col in self.layout.back_color:
                bg_luminance = self._get_luminance(bg_col)
                if bg_luminance > luminance:
                    luminance = bg_luminance
        else:
            luminance = self._get_luminance(self.back_color)

        if self.debug:
            self.print("Determine text color: luminance " + repr(luminance) + " for back color(s) " + repr(self.back_color))

        if luminance < 140:
            return Colors.WHITE
        else:
            return Colors.BLACK
        
    # Get the luminance of a color, in range [0..255]. 
    def _get_luminance(self, color):
        return color[0] * 0.2126 + color[1] * 0.7151 + color[2] * 0.0721


###########################################################################################################################


# Contains a list of display elements. If template_element is given, this element is
# never used itself but cloned for creating 
class DisplaySplitContainer(HierarchicalDisplayElement):
    
    HORIZONTAL = 0
    VERTICAL = 1

    def __init__(self, direction = 0, bounds = DisplayBounds(), name = "", id = 0):
        super().__init__(bounds, name, id)

        self.direction = direction
    
    # Updates the bounds of the children after adding or setting new ones
    def add(self, child):
        super().add(child)
        self.bounds_changed()

    # Updates the bounds of the children after adding or setting new ones
    def set(self, element, index):
        super().set(element, index)
        self.bounds_changed()

    # Update dimensions of all contained elements
    def bounds_changed(self):
        active_children = [x for x in self.children if x != None]

        if len(active_children) == 0:
            return
        
        # Currently, only horizontally placed segments are possible. May be changed by adding
        # a parameter.
        if self.direction == DisplaySplitContainer.HORIZONTAL:
            # Horizontal
            slot_width = int(self.width / len(active_children))
            slot_height = self.height

            for i in range(len(self.children)):
                element = self.children[i]
                if not element:
                    continue

                element.bounds = DisplayBounds(
                    self.x + i * slot_width,
                    self.y,
                    slot_width,
                    slot_height
                )
        else:
            # Vertical
            slot_width = self.width
            slot_height = int(self.height / len(active_children))

            for i in range(len(self.children)):
                element = self.children[i]
                if not element:
                    continue

                element.bounds = DisplayBounds(
                    self.x,
                    self.y + i * slot_height,
                    slot_width,
                    slot_height
                )


###########################################################################################################################


# DisplayLabel which is connected to a client parameter
class ParameterDisplayLabel(DisplayLabel, Updateable, ClientRequestListener):
    
    # parameter: {
    #     "mapping":     A ClientParameterMapping instance whose values should be shown in the area
    #     "depends":     Optional. If a ClientParameterMapping instance is passed, the display is only updated
    #                    when this mapping's value has changed.
    #     "textOffline": Text to show initially and when the client is offline
    #     "textReset":   Text to show when a reset happened (on rig changes etc.)
    # }
    def __init__(self, parameter, bounds = DisplayBounds(), layout = {}, name = "", id = 0):
        super().__init__(bounds=bounds, layout=layout, name=name, id=id)

        self._mapping = parameter["mapping"]
        self._depends = Tools.get_option(parameter, "depends", None)

        self._last_value = None
        self._depends_last_value = None

        self._text_offline = Tools.get_option(parameter, "textOffline", "")
        self._text_reset = Tools.get_option(parameter, "textReset", "")        
    
    # We need access to the client, so we store appl here
    def init(self, ui, appl):
        super().init(ui, appl)

        self.text = self._text_offline
        
        self._appl = appl
        self._debug = Tools.get_option(appl.config, "debugParameters", False)

    # Called on every update tick
    def update(self):
        if not self._depends:
            self._appl.client.request(self._mapping, self)
        else:
            self._appl.client.request(self._depends, self)

    # Reset the parameter display
    def reset(self):
        self._last_value = None
        self._depends_last_value = None
        self.text = self._text_reset

        if self._debug:
            self._print(" -> Reset parameter " + self._mapping.name)

    # Listen to client value returns (rig name and date)
    def parameter_changed(self, mapping):
        if mapping == self._mapping and mapping.value != self._last_value:
            # Main mapping changed
            if self._debug:
                self._print(" -> " + mapping.name + " has changed: " + repr(mapping.value))

            self._last_value = mapping.value

            # Set value on display
            self.text = mapping.value

        if mapping == self._depends and mapping.value != self._depends_last_value:
            # Dependency has changed: Request update of main mapping
            if self._debug:
                self._print("   -> Dependency (" + mapping.name + ") has changed to " + repr(mapping.value) + ", requesting " + self._mapping.name + "...")

            self._depends_last_value = mapping.value        
            
            self._appl.client.request(self._mapping, self)

    # Called when the client is offline (requests took too long)
    def request_terminated(self, mapping):
        self.text = self._text_offline

        self._last_value = None
        self._depends_last_value = None

        if self._debug:
            self._print(" -> Request for " + mapping.name + " failed, is the device offline?")

    # Debug console output
    def _print(self, msg):
        Tools.print(self.__class__.__name__ + ": " + msg)


###########################################################################################################################


# Factor by which the performance display (dot) is diminished in every update run. Set to 0 to disable, 1 to only show the maximum.
# Range: [0..1]
DEFAULT_PERFORMANCE_DOT_REDUCE_FACTOR = 0


# Shows a small dot indicating loop processing time (not visible when max. tick time is way below the updateInterval, warning
# the user when tick time gets higher and shows an alert when tick time is higher than the update interval, which means that
# the device is running on full capacity. If tick time is more than double the update interval, an even more severe alert is shown)
class PerformanceIndicator(HierarchicalDisplayElement, RuntimeMeasurementListener):

    def __init__(self, measurement, bounds = DisplayBounds(), name = "", id = 0, delay_factor = DEFAULT_PERFORMANCE_DOT_REDUCE_FACTOR):
        super().__init__(bounds, name, id)

        if not isinstance(measurement, RuntimeMeasurement):
            raise Exception("This can only be used with RuntimeMeasurements")

        self._measurement = measurement
        self._measurement.add_listener(self)

        self._dot = DisplayCircle(
            bounds = self.bounds,
            color = (0, 0, 0),
            name = "Dot"
        )

        # Display delay
        self._max = 0
        self._reduce_factor = delay_factor

        self.add(self._dot)

    # Add measurements to controller
    def init(self, ui, appl):
        super().init(ui, appl)

        appl.add_runtime_measurement(self._measurement)

    def measurement_updated(self, measurement):
        self._update_dot()

    # Called after the bounds have been changed
    def bounds_changed(self):
        self._dot.bounds = self.bounds

    # Called to show statistics
    def _update_dot(self):
        tick_percentage = self._delay(self._measurement.value() / self._measurement.interval_millis)
        
        if tick_percentage <= 1.0:
            self._dot.color = (0, 0, 0)

        elif tick_percentage <= 2.0:
            self._dot.color = self._fade_colors((0, 0, 0), (120, 120, 0), (tick_percentage - 1.0))

        elif tick_percentage <= 4.0:
            self._dot.color = self._fade_colors((120, 120, 0), (255, 0, 0), (tick_percentage - 2.0) / 2)

        else:
            self._dot.color = (255, 0, 0)
            
    # Dim the color
    def _fade_colors(self, color1, color2, factor):
        factor1 = 1 - factor
        factor2 = factor
        return (
            int(color1[0] * factor1 + color2[0] * factor2),
            int(color1[1] * factor1 + color2[1] * factor2),
            int(color1[2] * factor1 + color2[2] * factor2)
        )            
        
    def _delay(self, value):
        self._max *= self._reduce_factor

        if value > self._max:
            self._max = value

        return self._max
    

###########################################################################################################################


# DisplayLabel which is connected to a client parameter
class StatisticsDisplayLabel(DisplayLabel, RuntimeMeasurementListener, Updateable):
    
    def __init__(self, measurements, bounds = DisplayBounds(), layout = {}, id = 0):
        super().__init__(bounds=bounds, layout=layout, name="Statistics", id=id)        
    
        for m in measurements:
            if not isinstance(m, RuntimeMeasurement):
                continue
            
            m.add_listener(self)

        self._measurements = measurements

        self._texts = ["" for m in measurements]
        self._current_texts = ["" for m in measurements]

    # Add measurements to controller
    def init(self, ui, appl):
        super().init(ui, appl)

        for m in self._measurements:
            appl.add_runtime_measurement(m)

    def update(self):
        for i in range(len(self._texts)):
            if self._current_texts[i] != self._texts[i]:
                self._update_text()
                return

    def _update_text(self):
        lines = []
        for i in range(len(self._measurements)):
            self._current_texts[i] = self._texts[i]
            
            lines.append(self._texts[i])

        self.text = "\n".join(lines)    

    def measurement_updated(self, measurement):
        for i in range(len(self._measurements)):
            m = self._measurements[i]

            if not isinstance(m, RuntimeMeasurement):
                self._texts[i] = m.get_message()
            else:    
                if m != measurement:
                    continue
                
                self._texts[i] = m.get_message()
        
