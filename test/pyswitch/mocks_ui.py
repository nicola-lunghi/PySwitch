from lib.pyswitch.ui.elements.elements import HierarchicalDisplayElement
from lib.pyswitch.ui.elements.DisplayElement import DisplayBounds, DisplayElement
from lib.pyswitch.misc import Updateable

class MockDisplayElement(DisplayElement):
    pass


class MockUpdateableDisplayElement(DisplayElement, Updateable):
    def __init__(self, id = 0):
        super().__init__(id = id)

        self.num_update_calls = 0

    def update(self):
        self.num_update_calls += 1


class MockHierarchicalDisplayElement(HierarchicalDisplayElement):
    def __init__(self, bounds = DisplayBounds(), name = "", id = 0):
        super().__init__(bounds = bounds, name = name, id = id)

        self.num_print_calls = 0

    def print_debug_info(self, indentation = 0):
        self.num_print_calls += 1


class MockUserInterface:
    def __init__(self, width = 2000, height = 1000):
        self.num_show_calls = 0

        self.root = MockHierarchicalDisplayElement(
            bounds = DisplayBounds(0, 0, width, height)
        )

    def show(self, appl):
        self.num_show_calls += 1
        

