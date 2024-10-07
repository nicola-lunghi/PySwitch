from .base.Action import Action
from ...misc.Tools import Tools


# Simple action that prints a fixed text on the console (used for development)
class PrintAction(Action):    
    def push(self):
        print(Tools.get_option(self.config, "text", ""))

