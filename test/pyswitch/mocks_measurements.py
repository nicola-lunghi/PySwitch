
class MockRuntimeMeasurement:
    # type is arbitrary and only used externally
    def __init__(self, type = 0, interval_millis = 0):
        self.type = type
        self.interval_millis = interval_millis

        self.num_update_calls = 0
        self.num_start_calls = 0
        self.num_reset_calls = 0
        self.num_finish_calls = 0

        self.output_average = 0
        self.output_value = 0

        self.listeners = []

    # Average runtime
    @property
    def average(self):      
        return self.output_average
    
    def update(self):
        self.num_update_calls += 1

    @property
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

    def add_listener(self, listener):
        self.listeners.append(listener)


class MockMeasurements:
    RuntimeMeasurement = MockRuntimeMeasurement    
