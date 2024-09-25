from ..misc.Tools import Tools

# Periodic update helper    
class PeriodCounter:
    def __init__(self, interval_millis):
        self._interval_millis = int(interval_millis)

        self._last_reset = 0

    # Returns if the period has been exceeded. If yes, it lso resets
    # the period to the current time.
    @property
    def exceeded(self):
        current_time = Tools.get_current_millis()
        if self._last_reset + self._interval_millis < current_time:
            self._last_reset = current_time
            return True
        return False
            
