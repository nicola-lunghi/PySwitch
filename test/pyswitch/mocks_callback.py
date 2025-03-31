from lib.pyswitch.controller.callbacks import Callback


class MockCallback(Callback):
    def __init__(self, mappings = []):
        super().__init__(mappings)

        self.num_reset_calls = 0
    
    def reset(self):
        self.num_reset_calls += 1


class MockActionCallback(MockCallback):
    def __init__(self, mappings = []):
        super().__init__(mappings)

        self.update_displays_calls = 0

    def update_displays(self):
        self.update_displays_calls += 1


class MockPushButtonActionCallback(MockActionCallback):
    def __init__(self, mappings = []):
        super().__init__(mappings)

        self.state_changed_calls = 0

    def state_changed_by_user(self):
        self.state_changed_calls += 1


class MockSplashCallback(MockCallback):
    def __init__(self, mappings = [], output = None):
        super().__init__(mappings)

        self.output = output

    def get_root(self):
        return self.output
    

class MockEnabledCallback(MockCallback):
    def __init__(self, mappings = [], output = None):
        super().__init__(mappings)

        self.output = output
        self.enabled_calls = []

    def enabled(self, action):
        self.enabled_calls.append(action)
        return self.output
        

class MockDisplayLabelCallback(MockCallback):
    def __init__(self, mappings = [], label_text = None):
        super().__init__(mappings)

        self.update_label_calls = []
        self.label_text = label_text

    def update_label(self, label):
        self.update_label_calls.append(label)
        
        if self.label_text:
            label.text = self.label_text
