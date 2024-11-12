from displayio import Group
from adafruit_display_text import label, wrap_text_to_pixels
from adafruit_display_shapes.rect import Rect

from .ui import HierarchicalDisplayElement, DisplayBounds, DisplayElement

from ..controller.ConditionTree import ConditionTree, Condition
from ..controller.Client import BidirectionalClient
from ..misc import Updateable, Colors, get_option, do_print


# Data class for layouts
class DisplayLabelLayout:

    # layout:
    #  {
    #     "font": Path to the font, example: "/fonts/H20.pcf"
    #     "maxTextWidth": Maximum text width in pixels (default: 220) optional
    #     "lineSpacing": Line spacing (optional), float (default: 1)
    #     "textColor": Text color (default is auto)
    #     "backColor": Background color (default is none) Can be a tuple also to show a rainbow background
    #     "text": Initial text (default is none)
    #     "stroke": Amount of pixels to reduce from the background (fake frame, default: 0)
    # }
    def __init__(self, layout = {}):
        self.font_path = get_option(layout, "font", None)
        self.max_text_width = get_option(layout, "maxTextWidth")
        self.line_spacing = get_option(layout, "lineSpacing", 1)
        self.text = get_option(layout, "text", "")
        self.text_color = get_option(layout, "textColor", None)
        self.back_color = get_option(layout, "backColor", None)
        self.stroke = get_option(layout, "stroke", 0)

    # Check mandatory fields
    def check(self, label_id):
        if not self.font_path:
            raise Exception("Font missing: " + repr(label_id))


######################################################################################################################################


# Controller for a generic rectangular label on the user interface.
class DisplayLabel(DisplayElement): #, ConditionListener, ConditionTreeEntryReplacer):

    # Line feed used for display
    LINE_FEED = "\n"

    # layout can also be a Condition!
    def __init__(self, layout = None, bounds = DisplayBounds(), name = "", id = 0, scale = 1):
        super().__init__(bounds = bounds, name = name, id = id)

        self._scale = scale

        if isinstance(layout, Condition):
            self._layout_tree = ConditionTree(
                subject = layout,
                listener = self,
                replacer = self,
                allow_lists = False
            )

            self._layout = self._layout_tree.value
        else:
            self._layout_tree = None

            self._layout = DisplayLabelLayout(layout if layout else {})
            self._layout.check(self.id)

        self._initial_text_color = self._layout.text_color        
        self._ui = None    
        self._appl = None

        self._background = None 
        self._label = None      

    # Adds the slot to the splash
    def init(self, ui, appl):
        self._ui = ui
        self._appl = appl

        if self._layout_tree:
            self._layout_tree.init(appl)

        self._update_font()

        # Append background, if any
        if self.back_color:
            self._background = Rect(
                x = self.bounds.x + self._layout.stroke, 
                y = self.bounds.y + self._layout.stroke,
                width = self.bounds.width - self._layout.stroke * 2, 
                height = self.bounds.height - self._layout.stroke * 2, 
                fill = self.layout.back_color
            )
            ui.splash.append(self._background)

        # Trigger automatic text color determination
        self.text_color = self.layout.text_color

        # Trigger text wrapping
        self.text = self.layout.text

        # Append text area
        self._label = label.Label(
            self._font,
            anchor_point = (0.5, 0.5), 
            anchored_position = (
                int(self.bounds.width / 2), 
                int(self.bounds.height / 2)
            ),
            text = self._wrap_text(self.layout.text),
            color = self.layout.text_color,
            line_spacing = self.layout.line_spacing,
            scale = self._scale
        )
        
        group = Group(
            scale = 1, 
            x = self.bounds.x, 
            y = self.bounds.y
        )
        group.append(self._label)

        # Adds all backgrounds and the frame to the splash
        super().init(ui, appl)

        # Add label (group) to splash        
        ui.splash.append(group)

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
                if not self._layout.text_color:
                    self._layout.text_color = self._determine_text_color()

                self._label.color = self._layout.text_color
                self._initial_text_color = self._layout.text_color

        # Changes to the backgrounds
        if self._layout.back_color:
            # Back color changed?
            if old.back_color and old.back_color != self._layout.back_color:
                if self._background:
                    self._background.fill = self._layout.back_color

                # Update text color, too (might change when no initial color has been set)
                self.text_color = self._initial_text_color

    @property
    def back_color(self):
        return self.layout.back_color

    @back_color.setter
    def back_color(self, color):
        if self.layout.back_color and not color:
            return
        #    raise Exception("You can not remove a background (set color to black instead)")            

        if not self.layout.back_color and color:
            return
        #    raise Exception("You can only change the background color if an initial background color has been passed")
        
        if self.layout.back_color == color:
            return

        self.layout.back_color = color

        if self._background:
            self._background.fill = color

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
        
        self.layout.text_color = text_color

        if self._label:
            self._label.color = text_color

    @property
    def text(self):
        return self.layout.text

    @text.setter
    def text(self, text):
        # In case of low memory detected by the controller, we just show this information
        if self._appl and self._appl.low_memory_warning:
            text = "Low Memory!"
        
        if self.layout.text == text:
            return
        
        self.layout.text = text

        if self._label:
            self._label.text = self._wrap_text(text)

    # Wrap text if requested
    def _wrap_text(self, text):
        if not text:
            return ""
        
        if self.layout.max_text_width:
            return DisplayLabel.LINE_FEED.join(
                wrap_text_to_pixels(
                    text, 
                    self.layout.max_text_width,
                    self._font
                )
            )
        else:
            return text

    # Determines a matching text color to the current background color.
    # Algorithm adapted from https://nemecek.be/blog/172/how-to-calculate-contrast-color-in-python
    def _determine_text_color(self):
        if not self.back_color:
            return Colors.WHITE
        
        luminance = self.back_color[0] * 0.2126 + self.back_color[1] * 0.7151 + self.back_color[2] * 0.0721

        if luminance < 140:
            return Colors.WHITE
        else:
            return Colors.BLACK        


###########################################################################################################################


# Contains a list of display elements. If template_element is given, this element is
# never used itself but cloned for creating 
class DisplaySplitContainer(HierarchicalDisplayElement):
    
    HORIZONTAL = 0
    VERTICAL = 1

    def __init__(self, direction = 0, bounds = DisplayBounds(), name = "", id = 0, children = None):
        super().__init__(bounds = bounds, name = name, id = id, children = children)

        self.direction = direction
    
    # Add a child element
    def add(self, child):
        super().add(child)
        self.bounds_changed()

    # Sets a child element at the given index
    def set(self, element, index):
        super().set(element, index)
        self.bounds_changed()

    # Update dimensions of all contained elements
    def bounds_changed(self):
        super().bounds_changed()
        
        active_children = [x for x in self.children if x != None]

        if len(active_children) == 0:
            return
        
        # Currently, only horizontally placed segments are possible. May be changed by adding
        # a parameter.
        if self.direction == DisplaySplitContainer.HORIZONTAL:
            # Horizontal
            slot_width = int(self.bounds.width / len(active_children))

            for i in range(len(active_children)):
                active_children[i].bounds = DisplayBounds(
                    self.bounds.x + i * slot_width,
                    self.bounds.y,
                    slot_width,
                    self.bounds.height
                )
        else:
            # Vertical
            slot_height = int(self.bounds.height / len(active_children))

            for i in range(len(active_children)):
                active_children[i].bounds = DisplayBounds(
                    self.bounds.x,
                    self.bounds.y + i * slot_height,
                    self.bounds.width,
                    slot_height
                )


###########################################################################################################################


# DisplayLabel which is connected to a client parameter
class ParameterDisplayLabel(DisplayLabel, Updateable): #, ClientRequestListener):
    
    # parameter: {
    #     "mapping":     A ClientParameterMapping instance whose values should be shown in the area
    #     "depends":     Optional. If a ClientParameterMapping instance is passed, the display is only updated
    #                    when this mapping's value has changed.
    #     "textOffline": Text to show initially and when the client is offline (optional)
    #     "textReset":   Text to show when a reset happened (on rig changes etc.). Optional.
    # }
    def __init__(self, parameter, bounds = DisplayBounds(), layout = {}, name = "", id = 0):
        DisplayLabel.__init__(self, bounds = bounds, layout = layout, name = name, id = id)

        self._mapping = parameter["mapping"]
        self._depends = get_option(parameter, "depends", None)

        self._last_value = None
        self._depends_last_value = None

        self._text_offline = get_option(parameter, "textOffline", "")
        self._text_reset = get_option(parameter, "textReset", "")        
    
    # We need access to the client, so we store appl here
    def init(self, ui, appl):
        super().init(ui, appl)

        self.text = self._text_offline
        self._appl = appl

        self._appl.client.register(self._mapping, self)
        
        if self._depends:
            self._appl.client.register(self._depends, self)
        
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

    # Listen to client value returns (rig name and date)
    def parameter_changed(self, mapping):
        if mapping == self._mapping and mapping.value != self._last_value:
            # Main mapping changed
            self._last_value = mapping.value

            # Set value on display
            self.text = mapping.value

        if mapping == self._depends and mapping.value != self._depends_last_value:
            # Dependency has changed: Request update of main mapping
            self._depends_last_value = mapping.value        
            
            self._appl.client.request(self._mapping, self)

    # Called when the client is offline (requests took too long)
    def request_terminated(self, mapping):
        self.text = self._text_offline

        self._last_value = None
        self._depends_last_value = None


###########################################################################################################################


class TunerDevianceDisplay(DisplayElement):

    # Defines what to show as "in tune" (green). Aligned to a PolyTune tuner.
    IN_TUNE_ABOVE = 7935  # = 7945 - 10;  109.9 Hz;
    IN_TUNE_BELOW = 8444  # = 8434 + 10;  110.1 Hz;

    def __init__(self, 
                 bounds, 
                 zoom,
                 width, 
                 id = 0
        ):
        DisplayElement.__init__(self, bounds = bounds, id = id)

        self.width = width
        self._zoom = zoom

        self._current_color = None
        self.in_tune = False

    def init(self, ui, appl):
        DisplayElement.init(self, ui, appl)
        
        self._marker_intune = Rect(
            x = int((self.bounds.width - self.width) * 0.5),
            y = self.bounds.y,
            width = self.width,
            height = self.bounds.height,
            fill = TunerDisplay.COLOR_NEUTRAL
        )

        ui.splash.append(self._marker_intune)

        self._marker = Rect(
            x = int((self.bounds.width - self.width) * 0.5),
            y = self.bounds.y,
            width = self.width,
            height = self.bounds.height,
            fill = TunerDisplay.COLOR_IN_TUNE
        )
        self._current_color = self._marker.fill

        ui.splash.append(self._marker)

    # Sets deviance value in range [0..16383]
    def set(self, value):
        value_scaled = value
        if self._zoom != 1:
            value_scaled = max(-8192, min(int((value - 8192) * self._zoom), 8192)) + 8191

        self._marker.x = int((self.bounds.width - self.width) * value_scaled / 16384)

        if value >= self.IN_TUNE_ABOVE and value <= self.IN_TUNE_BELOW:
            self.in_tune = True
            self.set_color(TunerDisplay.COLOR_IN_TUNE)
        else:
            self.in_tune = False
            self.set_color(TunerDisplay.COLOR_OUT_OF_TUNE)

    # Sets the color
    def set_color(self, color):
        if self._current_color == color:
            return
        
        self._current_color = color
        self._marker.fill = color


###########################################################################################################################


class TunerDisplay(HierarchicalDisplayElement):

    # Note names 
    _TUNER_NOTE_NAMES = ('C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B')     # (jazz man's variant)
    #_TUNER_NOTE_NAMES = ('C','C#','D','D#','E','F','F#','G','G#','A','A#','B')     # (sharp variant)

    COLOR_OUT_OF_TUNE = Colors.ORANGE
    COLOR_IN_TUNE = Colors.LIGHT_GREEN
    COLOR_NEUTRAL = Colors.WHITE

    def __init__(self, 
                 mapping_note, 
                 mapping_deviance = None, 
                 bounds = DisplayBounds(), 
                 layout = {}, 
                 scale = 1,                                # Scaling of the note display label
                 deviance_height = 40,                     # Height of the deviance display
                 deviance_width = 5,                       # Width of the deviance display pointer line and "in tune" marker
                 deviance_zoom = 2.4,                      # Scaling of values. Set to > 1 to make the tuner display more sensitive.
        ):
        HierarchicalDisplayElement.__init__(self, bounds = bounds)

        self._mapping_note = mapping_note
        self._mapping_deviance = mapping_deviance

        self.label_note = DisplayLabel(
            bounds = bounds,
            layout = layout,
            scale = scale
        )
        self.add(self.label_note)

        self._label_left = None
        self._label_right = None

        if self._mapping_deviance:
            self.deviance = TunerDevianceDisplay(
                bounds = bounds.bottom(deviance_height),
                width = deviance_width,
                zoom = deviance_zoom
            )            
            self.add(self.deviance)

        self._last_note = None
        self._last_deviance = 8192

    # We need access to the client, so we store appl here
    def init(self, ui, appl):
        HierarchicalDisplayElement.init(self, ui, appl)

        self._appl = appl
        
        self._appl.client.register(self._mapping_note, self)
        
        if self._mapping_deviance:
            self._appl.client.register(self._mapping_deviance, self)

    # Reset the display
    def reset(self):
        self._last_note = None
        self._last_deviance = 8192
        
        self.label_note.text = "-"
        self.label_note.text_color = self.COLOR_NEUTRAL

    # Listen to client value returns
    def parameter_changed(self, mapping):
        if mapping == self._mapping_note and mapping.value != self._last_note:
            self._last_note = mapping.value

            self.label_note.text = self._TUNER_NOTE_NAMES[mapping.value % 12]            

        if mapping == self._mapping_deviance and mapping.value != self._last_deviance:
            self._last_deviance = mapping.value        
            
            self.deviance.set(self._last_deviance)            

            # Enable this for calibration.
            #self._debug_calibration(mapping.value)            

            if self.deviance.in_tune:
                self.label_note.text_color = self.COLOR_IN_TUNE
            else:
                self.label_note.text_color = self.COLOR_OUT_OF_TUNE

    # Called when the client is offline (requests took too long)
    def request_terminated(self, mapping):
        pass                                       # pragma: no cover

    # For calibration: Shows statistics on the tuner deviance over a period of 4 seconds.
    #def _debug_calibration(self, value):
    #    if not hasattr(self, "_calib_period"):
    #        from ..misc import PeriodCounter
    #        self._calib_period = PeriodCounter(4000)
    #        self._min = 9999999
    #        self._max = -1
    #        self._sum = 0
    #        self._steps = 0
    #    
    #    self._sum += value
    #    self._steps += 1
    #
    #    if value > self._max:
    #        self._max = value
    #    if value < self._min:
    #        self._min = value
    #
    #    if self._calib_period.exceeded:
    #        avg = int(self._sum / self._steps)
    #        do_print("[ " + repr(self._min - avg) + " .. " + repr(self._max - avg) + " ] Avg: " + repr(avg))
    #
    #        self._min = 9999999
    #        self._max = -1
    #        self._sum = 0
    #        self._steps = 0


###########################################################################################################################


# Shows a small dot indicating loop processing time (not visible when max. tick time is way below the updateInterval, warning
# the user when tick time gets higher and shows an alert when tick time is higher than the update interval, which means that
# the device is running on full capacity. If tick time is more than double the update interval, an even more severe alert is shown)
class PerformanceIndicator(DisplayElement): #, RuntimeMeasurementListener):

    def __init__(self, measurement_id, bounds = DisplayBounds(), name = "", id = 0):
        super().__init__(bounds = bounds, name = name, id = id)

        self._measurement_id = measurement_id        

    # Add measurements to controller
    def init(self, ui, appl):
        super().init(ui, appl)

        r = int(self.bounds.width / 2) if self.bounds.width > self.bounds.height else int(self.bounds.height / 2)
        
        self._dot = Rect(
            x = self.bounds.x, 
            y = self.bounds.y,
            width = 2 * r,
            height = 2 * r,
            fill = (0, 0, 0)
        )
        ui.splash.append(self._dot)

        self._measurement = appl.get_measurement(self._measurement_id)
        self._measurement.add_listener(self)

    def measurement_updated(self, measurement):
        tick_percentage = self._measurement.value / self._measurement.interval_millis
        
        if tick_percentage <= 1.0:
            self._dot.fill = (0, 0, 0)

        elif tick_percentage <= 2.0:
            self._dot.fill = (120, 120, 0) #self._fade_colors((0, 0, 0), (120, 120, 0), (tick_percentage - 1.0))

        #elif tick_percentage <= 4.0:
        #    self._dot.fill = self._fade_colors((120, 120, 0), (255, 0, 0), (tick_percentage - 2.0) / 2)

        else:
            self._dot.fill = (255, 0, 0)
            
    # Dim the color
    #def _fade_colors(self, color1, color2, factor):
    #    factor1 = 1 - factor
    #    factor2 = factor
    #    return (
    #        int(color1[0] * factor1 + color2[0] * factor2),
    #        int(color1[1] * factor1 + color2[1] * factor2),
    #        int(color1[2] * factor1 + color2[2] * factor2)
    #    )            
        

###########################################################################################################################


# Label showing statistical info
#class StatisticsDisplayLabel(DisplayLabel, Updateable):  #RuntimeMeasurementListener
#    
#    def __init__(self, measurements, bounds = DisplayBounds(), layout = None, name = "", id = 0):
#        super().__init__(bounds = bounds, layout = layout, name = name, id = id)        
#    
#        for m in measurements:
#            if not isinstance(m, RuntimeMeasurement):
#                continue
#            
#            m.add_listener(self)
#
#        self._measurements = measurements
#
#        self._texts = ["" for m in measurements]
#        self._current_texts = ["" for m in measurements]
#
#    # Add measurements to controller
#    def init(self, ui, appl):
#        super().init(ui, appl)
#
#        for m in self._measurements:
#            appl.add_runtime_measurement(m)
#
#    def update(self):
#        for i in range(len(self._texts)):
#            if self._current_texts[i] != self._texts[i]:
#                self._update_text()
#                return
#
#    def _update_text(self):
#        lines = []
#        for i in range(len(self._measurements)):
#            self._current_texts[i] = self._texts[i]
#            
#            lines.append(self._texts[i])
#
#        self.text = "\n".join(lines)    
#
#    def measurement_updated(self, measurement):
#        for i in range(len(self._measurements)):
#            m = self._measurements[i]
#
#            if not isinstance(m, RuntimeMeasurement):
#                self._texts[i] = m.get_message()
#            else:    
#                if m != measurement:
#                    continue
#                
#                self._texts[i] = m.get_message()
        

###########################################################################################################################


# Shows a small dot indicating the bidirectional protocol state (does not show anything when bidirectional 
# communication is disabled)
class BidirectionalProtocolState(DisplayElement, Updateable):

    def __init__(self, bounds = DisplayBounds(), name = "", id = 0):
        DisplayElement.__init__(self, bounds = bounds, name = name, id = id)

        self._current_color = None

    def init(self, ui, appl):
        DisplayElement.init(self, ui, appl)
        self._appl = appl

        if not isinstance(self._appl.client, BidirectionalClient):
            return

        r = int(self.bounds.width / 2) if self.bounds.width > self.bounds.height else int(self.bounds.height / 2)
        
        self._dot = Rect(
            x = self.bounds.x, 
            y = self.bounds.y,
            width = 2 * r,
            height = 2 * r,
            fill = (0, 0, 0)
        )
        ui.splash.append(self._dot)

    def update(self):
        if not isinstance(self._appl.client, BidirectionalClient):
            return

        new_color = self._appl.client.protocol.get_color()

        if self._current_color == new_color:
            return

        self._current_color = new_color
        self._dot.fill = self._current_color
            
