from lib.pyswitch.ui.elements.elements import HierarchicalDisplayElement
from lib.pyswitch.ui.elements.DisplayElement import DisplayBounds, DisplayElement
from lib.pyswitch.misc import Updateable


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

        self.font_loader = MockFontLoader()
        self.splash = []

    def show(self, appl):
        self.num_show_calls += 1

        self.root.init(self, appl)

    def create_label(self, bounds = DisplayBounds(), layout = {}, name = "", id = 0):
        return MockDisplayLabel(bounds=bounds, layout=layout, name=name, id=id)
        

class MockDisplayLabel(DisplayElement):

    def __init__(self, bounds = DisplayBounds(), layout = {}, name = "", id = 0):
        super().__init__(bounds=bounds, name=name, id=id)

        self.output_back_color = (0, 0, 0)
        self.output_text = ""

        self.layout = layout

    @property
    def back_color(self):
        return self.output_back_color

    @back_color.setter
    def back_color(self, color):
        self.output_back_color = color

    @property
    def text(self):
        return self.output_text

    @text.setter
    def text(self, text):
        self.output_text = text


class MockFont:
    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return repr(self.path)


class MockFontLoader:
    def get(self, path):
        return MockFont(path)
