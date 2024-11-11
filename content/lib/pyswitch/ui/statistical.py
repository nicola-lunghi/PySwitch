from micropython import const

from .elements import PerformanceIndicator, BidirectionalProtocolState #, StatisticsDisplayLabel
from ..controller.measurements import RuntimeMeasurement #, FreeMemoryMeasurement
from ..controller.Controller import Controller


# Properties for the performance indicator (dot)
_PERFORMANCE_INDICATOR_SIZE = const(5)
_PERFORMANCE_INDICATOR_MARGIN = const(2)

# Properties of the statistics display label
#_STAT_HEIGHT = const(40)                 # Height


# Performance indicator (dot). Will be placed at the right upper corner of the passed bounds.
def PERFORMANCE_DOT(parent_bounds):
    return PerformanceIndicator(        
        measurement = RuntimeMeasurement(
            type = Controller.STAT_ID_TICK_TIME, 
            interval_millis = 200
        ),
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

# Statistics area. Will be placed at the top of the passed bounds.
#def STATS_DISPLAY(parent_bounds):
#    return StatisticsDisplayLabel(
#        bounds = parent_bounds.top(_STAT_HEIGHT),
#        layout = {
#            "font": "/fonts/A12.pcf",
#            "backColor": (50, 50, 50)
#        },
#        measurements = [
#            RuntimeMeasurement(
#                type = Controller.STAT_ID_TICK_TIME, 
#                interval_millis = 1000
#            ),
#            
#            #RuntimeMeasurement(                                     # This measurement costs a lot of overhead!
#            # type = Controller.STAT_ID_SWITCH_UPDATE_TIME, 
#            # interval_millis = 1000
#            # ),   
#            
#            FreeMemoryMeasurement()
#        ]
#    )
