from lib.pyswitch.ui.elements import HierarchicalDisplayElement
from lib.pyswitch.ui.ui import DisplayBounds, DisplayElement
from lib.pyswitch.misc import Updateable, Callback


class MockUpdateableDisplayElement(DisplayElement, Updateable):
    def __init__(self, id = 0):
        DisplayElement.__init__(self, id = id)

        self.num_update_calls = 0

    def update(self):
        self.num_update_calls += 1


class MockHierarchicalDisplayElement(HierarchicalDisplayElement):
    def __init__(self, bounds = DisplayBounds(), name = "", id = 0, children = None):
        super().__init__(bounds = bounds, name = name, id = id, children = children)

        self.num_print_calls = 0
        self.num_init_calls = 0
        self.num_bounds_changed_calls = 0

    def print_debug_info(self, indentation = 0):
        self.num_print_calls += 1

    def init(self, ui, appl):
        super().init(ui, appl)

        self.num_init_calls += 1

    def bounds_changed(self):
        super().bounds_changed()
        
        self.num_bounds_changed_calls += 1


class MockST7789:
    def __init__(self):
        self.show_calls = []

    def show(self, splash):
        self.show_calls.append(splash)


class MockDisplayDriver:
    def __init__(self, w = 0, h = 0, init = False):
        self.width = w
        self.height = h

        if init:
            self.init()

    def init(self):
        self.tft = MockST7789()


class MockUiController:
    def __init__(self, width = 2000, height = 1000, root = None):
        self.root = MockHierarchicalDisplayElement(
            bounds = DisplayBounds(0, 0, width, height)
        ) if not root else root

    def search(self, id, index = None):
        return self.root.search(id, index)
    
    def create_label(self, bounds = DisplayBounds(), layout = {}, name = "", id = 0):
        return MockDisplayLabel(bounds=bounds, layout=layout, name=name, id=id)

    def set_root(self, root):
        self.root = root

    def init(self, appl):
        pass

    def show(self):
        pass

    @property
    def bounds(self):
        return self.root.bounds
    

class MockDisplaySplash:
    def __init__(self, element = None):
        self.font_loader = MockFontLoader()

        self.splash = []

        self.root = element if element else MockHierarchicalDisplayElement()
        

class MockDisplayLabel(DisplayElement):

    def __init__(self, bounds = DisplayBounds(), layout = {}, name = "", id = 0):
        super().__init__(bounds = bounds, name = name, id = id)

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


class MockSplashCallback(Callback):
    def __init__(self, mappings = [], output = None):
        self.mappings = mappings
        self.output_get = output

    def get_mappings(self):
        return self.mappings
    
    def get(self):
        return self.output_get