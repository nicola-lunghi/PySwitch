from .Action import Action


# Action to explore switch GPIO assignments (used internally only in explore mode!)
class ExploreIoAction(Action):
    def trigger(self, event):
        print("Switch pressed: " + self.config["name"])

