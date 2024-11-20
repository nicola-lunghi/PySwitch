from lib.pyswitch.controller.actions.callbacks import Callback


class MockCallback(Callback):
    def __init__(self, mappings = None):
        super().__init__()

        self.mappings = mappings
        self.num_reset_calls = 0

    def get_mappings(self):
        if self.mappings:
            for m in self.mappings:
                yield m
        else:
            for m in super().get_mappings():
                yield m
    
    def reset(self):
        self.num_reset_calls += 1


class MockActionCallback(MockCallback):
    def __init__(self, mappings = None):
        super().__init__(mappings)

        self.update_displays_calls = []

    def update_displays(self, action):
        self.update_displays_calls.append(action)


class MockPushButtonActionCallback(MockActionCallback):
    def __init__(self, mappings = None):
        super().__init__(mappings)

        self.state_changed_calls = []

    def state_changed_by_user(self, action):
        self.state_changed_calls.append(action)


class MockSplashCallback(MockCallback):
    def __init__(self, mappings = None, output = None):
        super().__init__(mappings)

        self.output = output

    def get_root(self):
        return self.output
    

class MockEnabledCallback(MockCallback):
    def __init__(self, mappings = None, output = None):
        super().__init__(mappings)

        self.output = output
        self.enabled_calls = []

    def enabled(self, action):
        self.enabled_calls.append(action)
        return self.output
        