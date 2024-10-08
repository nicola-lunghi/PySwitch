from .elements.elements import StatisticsDisplayLabel, PerformanceIndicator
from ..core.controller.measurements import RuntimeMeasurement, FreeMemoryMeasurement
from ..core.controller.Controller import Controller


# Properties for the performance indicator (dot)
PERFORMANCE_INDICATOR_SIZE = 5
PERFORMANCE_INDICATOR_MARGIN = 2

# Properties of the statistics display label
STAT_HEIGHT = 40                 # Height
STAT_LINES = 3                   # Statistics number of lines


# Pre-defines some usefule statistics display elements to be used in Setup["displays"]
class StatisticalDisplays:
    # Performance indicator (dot). Will be placed at the right upper corner of the passed bounds.
    @staticmethod
    def PERFORMANCE_DOT(parent_bounds):
        return PerformanceIndicator(        
            measurement = RuntimeMeasurement(
                type = Controller.STAT_ID_TICK_TIME, 
                interval_millis = 200
            ),
            name = "Dot",
            bounds = parent_bounds.top(
                    PERFORMANCE_INDICATOR_SIZE
                ).right(
                    PERFORMANCE_INDICATOR_SIZE
                ).translated(
                    - PERFORMANCE_INDICATOR_MARGIN, 
                    PERFORMANCE_INDICATOR_MARGIN
                )
        )

    # Statistics area. Will be placed at the top of the passed bounds.
    @staticmethod
    def STATS_DISPLAY(parent_bounds):
        return StatisticsDisplayLabel(
            bounds = parent_bounds.top(STAT_HEIGHT * STAT_LINES),
            layout = {
                "font": "/fonts/A12.pcf"
            },
            measurements = [
                RuntimeMeasurement(
                    type = Controller.STAT_ID_TICK_TIME, 
                    interval_millis = 1000
                ),
                
                #RuntimeMeasurement(                                     # This measurement costs a lot of overhead!
                # type = Controller.STAT_ID_SWITCH_UPDATE_TIME, 
                # interval_millis = 1000
                # ),   
                
                FreeMemoryMeasurement()
            ]
        )