
# Handles all conditions to be updated
class Conditions:
    def __init__(self):
        self._conditions = []

    # Adds a Condition instance
    def add(self, condition):
        self._conditions.append(condition)

    # Called on every update tick
    def update(self):
        for condition in self._conditions:
            condition.update()
