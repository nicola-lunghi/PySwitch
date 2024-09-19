from ..Tools import Tools
from .DisplayLabel import DisplayLabel

# Contains a list of DisplayLabel instances.
class DisplayArea:

    def __init__(self, ui, config):
        self._ui = ui
        self._config = config
        self._content = []

        self.id = self._config["id"]
        
        self.x = int(self._config["x"])
        self.y = int(self._config["y"])

        self.width = int(self._config["width"])
        self.height = int(self._config["height"])

    # Returns the label at position index
    def get(self, index):
        while index >= len(self._content):
            self._content.append(self._create_label())

        self._update_dimensions()

        return self._content[index]

    # Create the labels in one area
    def _create_label(self):
        slot_layout = self._config["layout"]

        name = Tools.get_option(self._config, "name", "UnknownLabel")

        return DisplayLabel(
            self._ui, 
            self.x,
            self.y,
            self.width,
            self.height,
            slot_layout,
            id = name + " | " + str(len(self._content))
        )

    # Update label dimensions
    def _update_dimensions(self):
        if len(self._content) == 0:
            return
        
        slot_width = int(self.width / len(self._content))
        slot_height = self.height

        for i in range(len(self._content)):
            label = self._content[i]
            label.set_dimensions(
                self.x + i * slot_width,
                self.y,
                slot_width,
                slot_height
            )

    @property
    def back_color(self):
        if len(self._content) == 0: 
            return None
        return self._content[0].back_color

    @back_color.setter
    def back_color(self, color):
        for label in self._content:
            label.back_color = color

    @property
    def text_color(self):
        if len(self._content) == 0: 
            return None
        return self._content[0].text_color        

    @text_color.setter
    def text_color(self, color):
        for label in self._content:
            label.text_color = color        

    @property
    def corner_radius(self):
        if len(self._content) == 0: 
            return None
        return self._content[0].corner_radius        
    
    @corner_radius.setter
    def corner_radius(self, r):
        for label in self._content:
            label.corner_radius = r        

    @property
    def text(self):
        if len(self._content) == 0: 
            return None
        return self._content[0].text   

    @text.setter
    def text(self, text):
        for label in self._content:
            label.text = text  