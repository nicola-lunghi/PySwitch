
from .Action import Action
from ..Tools import Tools

# Simple action that prints a fixed text on the console
class PrintAction(Action):    
    def down(self):
        print(Tools.get_option(self.config, "text", ""))

