
from .base.HierarchicalDisplayElement import HierarchicalDisplayElement
from .DisplayCircle import DisplayCircle
from ..DisplayBounds import DisplayBounds
from ...definitions import DisplayConstants
from ...core.misc.Tools import Tools
from ...core.controller.measurements import RuntimeMeasurement
from ...core.controller.measurements import RuntimeMeasurementListener


# Shows a small dot indicating loop processing time (not visible when max. tick time is way below the updateInterval, warning
# the user when tick time gets higher and shows an alert when tick time is higher than the update interval, which means that
# the device is running on full capacity. If tick time is more than double the update interval, an even more severe alert is shown)
class PerformanceIndicator(HierarchicalDisplayElement, RuntimeMeasurementListener):

    def __init__(self, measurement, bounds = DisplayBounds(), name = "", id = 0, delay_factor = DisplayConstants.PERFORMANCE_DOT_REDUCE_FACTOR):
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