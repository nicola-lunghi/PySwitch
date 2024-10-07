from .base.HierarchicalDisplayElement import HierarchicalDisplayElement
from ..DisplayBounds import DisplayBounds

# Contains a list of display elements. If template_element is given, this element is
# never used itself but cloned for creating 
class DisplaySplitContainer(HierarchicalDisplayElement):
    
    HORIZONTAL = 0
    VERTICAL = 1

    def __init__(self, direction = 0, bounds = DisplayBounds(), name = "", id = 0):
        super().__init__(bounds, name, id)

        self.direction = direction
    
    # Updates the bounds of the children after adding or setting new ones
    def add(self, child):
        super().add(child)
        self.bounds_changed()

    # Updates the bounds of the children after adding or setting new ones
    def set(self, element, index):
        super().set(element, index)
        self.bounds_changed()

    # Update dimensions of all contained elements
    def bounds_changed(self):
        active_children = [x for x in self.children if x != None]

        if len(active_children) == 0:
            return
        
        # Currently, only horizontally placed segments are possible. May be changed by adding
        # a parameter.
        if self.direction == DisplaySplitContainer.HORIZONTAL:
            # Horizontal
            slot_width = int(self.width / len(active_children))
            slot_height = self.height

            for i in range(len(self.children)):
                element = self.children[i]
                if not element:
                    continue

                element.bounds = DisplayBounds(
                    self.x + i * slot_width,
                    self.y,
                    slot_width,
                    slot_height
                )
        else:
            # Vertical
            slot_width = self.width
            slot_height = int(self.height / len(active_children))

            for i in range(len(self.children)):
                element = self.children[i]
                if not element:
                    continue

                element.bounds = DisplayBounds(
                    self.x,
                    self.y + i * slot_height,
                    slot_width,
                    slot_height
                )
