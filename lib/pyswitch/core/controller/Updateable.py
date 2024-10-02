
# Base class for everything that needs to be updated regularily
class Updateable:
    def update(self):
        pass

    def reset(self):
        pass


###################################################################################


# Base class for handling updateables
class Updater:
    def __init__(self):
        self._updateables = []

    @property
    def updateables(self):
        return self._updateables

    # Add a new Updateable
    def add_updateable(self, u):
        self._updateables.append(u)

    # Update all updateables
    def update(self):
        for u in self._updateables:
            u.update()

    # Reset all updateables
    def reset(self):
        for u in self._updateables:
            u.reset()
