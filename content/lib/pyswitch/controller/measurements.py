from gc import collect, mem_free

from ..misc import Tools, EventEmitter, Updateable


# Base class for measurements
class StatisticsMeasurement:
    def __init__(self):
        self.reset()

    def value(self):
        return 0      # pragma: no cover

    def update(self):
        pass          # pragma: no cover

    # Reset measurement
    def reset(self):
        pass          # pragma: no cover

    # Generate output message
    def get_message(self):
        return ""     # pragma: no cover


#########################################################################


# Measurement of runtimes 
class RuntimeMeasurement(StatisticsMeasurement, EventEmitter, Updateable):
    
    # type is arbitrary and only used externally
    def __init__(self, interval_millis, type = ""):
        StatisticsMeasurement.__init__(self)
        EventEmitter.__init__(self) #, RuntimeMeasurementListener)

        self.type = type

        self.interval_millis = interval_millis
        self._last_output = 0

        self.reset()

    # Average runtime
    @property
    def average(self):
        if self._time_num == 0:
            return 0
        return int(self._time_aggr / self._time_num)
    
    def update(self):
        current = Tools.get_current_millis()
        if self._last_output + self.interval_millis < current:
            self._last_output = current

            for l in self.listeners:
                l.measurement_updated(self)

            self.reset()

    def value(self):
        return self.max

    # Initialize the instance
    def reset(self):
        self.max = 0         # Maximum runtime
        self.start_time = 0  # Start time
        self.end_time = 0    # End time

        self._time_aggr = 0  # Times added up
        self._time_num = 0   # Number of times added up

    # Start the measurement
    def start(self):
        self.start_time = Tools.get_current_millis()

    # End the measurement
    def finish(self):
        if self.start_time == 0:
            return
        
        self._add()  

    # Adds the current diff to the haystack
    def _add(self):
        self.end_time = Tools.get_current_millis()
        
        diff = self.end_time - self.start_time
        if diff > self.max:
            self.max = diff

        self._time_aggr = self._time_aggr + diff
        self._time_num = self._time_num + 1

    # Generate output message
    def get_message(self):
        if self._time_num == 0:
            return "No data"
        
        return repr(self.type) + ": Max " + str(self.max) + "ms, Avg " + str(self.average) + "ms"


################################################################################


# Listener for runtime measurement changes
#class RuntimeMeasurementListener:
#    def measurement_updated(self, measurement):
#        pass


################################################################################


# Measurement of free memory
class FreeMemoryMeasurement(StatisticsMeasurement):

    # Generate output message
    def get_message(self):
        return "Free " + Tools.format_size(self.value())
    
    def value(self):
        return self._get_free_memory_bytes()

    # Returns the available memory
    def _get_free_memory_bytes(self):
        collect()
        return mem_free()

