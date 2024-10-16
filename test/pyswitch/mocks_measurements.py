from lib.pyswitch.misc import Updateable
from lib.pyswitch.controller.measurements import StatisticsMeasurement

class MockMeasurements:
    
    StatisticsMeasurement = StatisticsMeasurement

    class RuntimeMeasurement(StatisticsMeasurement, Updateable):
        # type is arbitrary and only used externally
        def __init__(self, type = 0):
            self.type = type

            self.num_update_calls = 0
            self.num_start_calls = 0
            self.num_reset_calls = 0
            self.num_finish_calls = 0

            StatisticsMeasurement.__init__(self)

            self.output_average = 0
            self.output_value = 0
            self.output_message = ""

        # Average runtime
        @property
        def average(self):
            return self.output_average
        
        def update(self):
            self.num_update_calls += 1

        def value(self):
            return self.output_value

        # Initialize the instance
        def reset(self):
            self.num_reset_calls += 1

        # Start the measurement
        def start(self):
            self.num_start_calls += 1

        # End the measurement
        def finish(self):
            self.num_finish_calls += 1

        # Generate output message
        def get_message(self):
            return self.output_message

