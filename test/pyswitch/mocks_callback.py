from lib.pyswitch.misc import Callback


class MockCallback(Callback):
    def __init__(self, mappings = None, output = None):
        super().__init__()

        self.mappings = mappings
        self.output_get = output
        self.get_calls = []

    def get_mappings(self):
        if self.mappings:
            return self.mappings
        else:
            return super().get_mappings()
    
    def get(self, data):
        self.get_calls.append(data)
        return self.output_get