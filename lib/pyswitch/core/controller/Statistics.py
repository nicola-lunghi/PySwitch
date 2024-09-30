from ..misc.Tools import Tools
from ..misc.EventEmitter import EventEmitter

# Main application class (controls the processing)    
class Statistics(EventEmitter):
    def __init__(self, interval_millis):
        super().__init__(StatisticsListener)

        self._interval_millis = interval_millis
        self._last_output = 0

        self.reset()

    # Start a measurement
    def start(self):
        self._start_time = Tools.get_current_millis()

    # End a measurement
    def finish(self):
        self._add()

        if self._last_output + self._interval_millis < self._end_time:
            self._last_output = self._end_time

            self._show()
            self.reset()

    # Initialize the instance
    def reset(self):
        self._time_aggr = 0  # Times added up
        self._time_num = 0   # Number of times added up
        self._max = 0        # Max time

    @property
    def average(self):
        return int(self._time_aggr / self._time_num)
    
    @property
    def max(self):
        return self._max

    # Adds the current diff to the haystack
    def _add(self):
        self._end_time = Tools.get_current_millis()
        
        diff = self._end_time - self._start_time
        if diff > self._max:
            self._max = diff

        self._time_aggr = self._time_aggr + diff
        self._time_num = self._time_num + 1

    # Shows the stats (called in intervals) either on the assigned diplay element
    # or (if none has been passed on initialization) on the console
    def _show(self):
        # Call the listeners
        for listener in self.listeners:
            listener.update_statistics(self)

    # Render the output string
    def get_message(self):
        if self._time_num == 0:
            return "No data"
        
        return "Max " + str(self.max) + "ms, Avg " + str(self.average)


###########################################################################################


# Output for statistics
class StatisticsListener:
    def update_statistics(self, statistics):
        pass