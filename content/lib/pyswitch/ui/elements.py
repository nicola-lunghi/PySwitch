from micropython import const
from displayio import Group
from adafruit_display_text import label, wrap_text_to_pixels
from adafruit_display_shapes.rect import Rect

from .ui import HierarchicalDisplayElement, DisplayBounds, DisplayElement

from ..controller.Client import BidirectionalClient
from ..controller.Controller import Controller
from ..misc import Updateable, Colors, get_option #, do_print


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
class DisplayLabel(DisplayElement):

    # Line feed used for display
    LINE_FEED = "\n"

    def __init__(self, layout = None, bounds = DisplayBounds(), name = "", id = 0, scale = 1, callback = None):
        super().__init__(bounds = bounds, name = name, id = id)

        self._layout = DisplayLabelLayout(layout if layout else {})
        self._layout.check(self.id)
        self._initial_text_color = self._layout.text_color        

        self._scale = scale
        self._callback = callback

        self._ui = None    
        self._appl = None
        self._background = None 
        self._label = None
        
    # Adds the slot to the splash
    def init(self, ui, appl):
        self._ui = ui
        self._appl = appl

        self._update_font()

        if self._callback:
            that = self

            class _CallbackMappingListener:
                def parameter_changed(self, mapping):
                    that._callback.update_label(that)

                def request_terminated(self, mapping):
                    that._callback.update_label(that)       

            self._callback.init(appl, _CallbackMappingListener())

        # Append background, if any
        if self._layout.back_color:
            self._background = Rect(
                x = self.bounds.x + self._layout.stroke, 
                y = self.bounds.y + self._layout.stroke,
                width = self.bounds.width - self._layout.stroke * 2, 
                height = self.bounds.height - self._layout.stroke * 2, 
                fill = self._layout.back_color
            )
            ui.splash.append(self._background)

        # Trigger automatic text color determination
        self.text_color = self._layout.text_color

        # Trigger text wrapping
        self.text = self._layout.text

        # Append text area
        self._label = label.Label(
            self._font,
            anchor_point = (0.5, 0.5), 
            anchored_position = (
                int(self.bounds.width / 2), 
                int(self.bounds.height / 2)
            ),
            text = self._wrap_text(self._layout.text),
            color = self._layout.text_color,
            line_spacing = self._layout.line_spacing,
            scale = self._scale
        )
        
        group = Group(
            scale = 1, 
            x = self.bounds.x, 
            y = self.bounds.y
        )
        group.append(self._label)
        ui.splash.append(group)

        super().init(ui, appl)

    # Update font according to layout
    def _update_font(self):
        self._font = self._ui.font_loader.get(self._layout.font_path)

    @property
    def back_color(self):
        return self._layout.back_color

    @back_color.setter
    def back_color(self, color):
        if self._layout.back_color and not color:            
            raise Exception() #"You can not remove a background (set color to black instead)")            

        if not self._layout.back_color and color:
            raise Exception() #"You can only change the background color if an initial background color has been passed")
        
        if self._layout.back_color == color:
            return

        self._layout.back_color = color

        if self._background:
            self._background.fill = color

        # Update text color, too (might change when no initial color has been set)
        self.text_color = self._initial_text_color

    @property
    def text_color(self):
        return self._layout.text_color

    @text_color.setter
    def text_color(self, color):
        text_color = color        
        if not text_color:
            text_color = self._determine_text_color()

        if self._layout.text_color == text_color:
            return
        
        self._layout.text_color = text_color

        if self._label:
            self._label.color = text_color

    @property
    def text(self):
        return self._layout.text

    @text.setter
    def text(self, text):
        # In case of low memory detected by the controller, we just show this information
        if self._appl and hasattr(self._appl, "low_memory_warning") and self._appl.low_memory_warning:
            text = "Low Memory!"
        
        if self._layout.text == text:
            return
        
        self._layout.text = text

        if self._label:
            self._label.text = self._wrap_text(text)

    # Wrap text if requested
    def _wrap_text(self, text):
        if not text:
            return ""
        
        if self._layout.max_text_width:
            return DisplayLabel.LINE_FEED.join(
                wrap_text_to_pixels(
                    text, 
                    self._layout.max_text_width,
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
        
        self.bounds_changed()
    
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
        
        bounds = self.bounds

        # Currently, only horizontally placed segments are possible. May be changed by adding
        # a parameter.
        if self.direction == DisplaySplitContainer.HORIZONTAL:
            # Horizontal
            slot_width = int(bounds.width / len(active_children))

            for i in range(len(active_children)):
                active_children[i].bounds = DisplayBounds(
                    bounds.x + i * slot_width,
                    bounds.y,
                    slot_width,
                    bounds.height
                )
        else:
            # Vertical
            slot_height = int(bounds.height / len(active_children))

            for i in range(len(active_children)):
                active_children[i].bounds = DisplayBounds(
                    bounds.x,
                    bounds.y + i * slot_height,
                    bounds.width,
                    slot_height
                )


###########################################################################################################################


# Defines what to show as "in tune" (green). Aligned to a PolyTune tuner.
IN_TUNE_ABOVE = const(7935)  # = 7945 - 10;  109.9 Hz;
IN_TUNE_BELOW = const(8444)  # = 8434 + 10;  110.1 Hz;


class TunerDevianceDisplay(DisplayElement):

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

        if value >= IN_TUNE_ABOVE and value <= IN_TUNE_BELOW:
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
        value = mapping.value

        if mapping == self._mapping_note and value != self._last_note:
            self._last_note = mapping.value

            self.label_note.text = self._TUNER_NOTE_NAMES[value % 12]            

        if mapping == self._mapping_deviance and value != self._last_deviance:
            self._last_deviance = value        
            
            self.deviance.set(self._last_deviance)            

            # Uncomment this for calibration.
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
            self._dot.fill = (120, 120, 0) 

        else:
            self._dot.fill = (255, 0, 0)
        

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
            

###########################################################################################################################


# Properties for the performance indicator (dot)
_PERFORMANCE_INDICATOR_SIZE = const(5)
_PERFORMANCE_INDICATOR_MARGIN = const(2)


# Performance indicator (dot). Will be placed at the right upper corner of the passed bounds.
def PERFORMANCE_DOT(parent_bounds):
    return PerformanceIndicator(        
        measurement_id = Controller.STAT_ID_TICK_TIME,
        #name = "PerformanceDot",
        bounds = parent_bounds.top(
                _PERFORMANCE_INDICATOR_SIZE
            ).right(
                _PERFORMANCE_INDICATOR_SIZE
            ).translated(
                - _PERFORMANCE_INDICATOR_MARGIN, 
                _PERFORMANCE_INDICATOR_MARGIN
            )
    )

# Bidirectional protocol state indicator (dot). Will be placed at the right upper corner of the passed bounds.
def BIDIRECTIONAL_PROTOCOL_STATE_DOT(parent_bounds):
    return BidirectionalProtocolState(        
        #name = "ProtocolDot",
        bounds = parent_bounds.top(
                _PERFORMANCE_INDICATOR_SIZE
            ).right(
                _PERFORMANCE_INDICATOR_SIZE
            ).translated(
                - _PERFORMANCE_INDICATOR_MARGIN, 
                _PERFORMANCE_INDICATOR_MARGIN
            )
    )

