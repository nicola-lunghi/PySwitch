from micropython import const

from .elements import PerformanceIndicator, BidirectionalProtocolState #, StatisticsDisplayLabel
from ..controller.Controller import Controller


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

