from ..misc import EventEmitter, Updateable, get_current_millis


# Measurement of runtimes 
class RuntimeMeasurement(EventEmitter, Updateable):  
    
    # type is arbitrary and only used externally
    def __init__(self, interval_millis):
        EventEmitter.__init__(self) #, RuntimeMeasurementListener)

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
        current = get_current_millis()
        if self._last_output + self.interval_millis < current:
            self._last_output = current

            for l in self.listeners:
                l.measurement_updated(self)

            self.reset()

    # Initialize the instance
    def reset(self):
        self.value = 0       # Maximum runtime
        self.start_time = 0  # Start time
        self.end_time = 0    # End time

        self._time_aggr = 0  # Times added up
        self._time_num = 0   # Number of times added up

    # Start the measurement
    def start(self):
        self.start_time = get_current_millis()

    # Adds the current diff to the haystack
    def finish(self):
        if self.start_time == 0:
            return
        
        self.end_time = get_current_millis()
        
        diff = self.end_time - self.start_time
        if diff > self.value:
            self.value = diff

        self._time_aggr = self._time_aggr + diff
        self._time_num = self._time_num + 1


################################################################################


# Listener for runtime measurement changes
#class RuntimeMeasurementListener:
#    def measurement_updated(self, measurement):
#        pass

