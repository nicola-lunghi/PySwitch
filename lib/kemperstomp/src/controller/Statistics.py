from ..Tools import Tools

# Main application class (controls the processing)    
class Statistics:
    def __init__(self, display_element = None):
        self._display_element = display_element        
        self._last_output = 0

        self.reset()

    # Start a measurement
    def start(self):
        self._start_time = Tools.get_current_millis()

    # End a measurement
    def finish(self):
        self._add()

        if self._last_output + 2 * 1000 < self._end_time:
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

    # Shows the stats (called in intervals)
    def _show(self):
        if self._display_element == None:
            print(self._get_str())
        else:
            self._display_element.text = self._get_str()

    # Render the output string
    def _get_str(self):
        if self._time_num == 0:
            return "No data"
        
        return "Max " + str(self.max) + "ms, Avg " + str(self.average)
