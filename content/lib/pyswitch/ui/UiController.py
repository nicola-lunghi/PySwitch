from .ui import DisplayBounds
from .elements import DisplayLabel
from ..controller.ConditionTree import ConditionTree
from ..misc import Updateable


class UiController:

    # Creates the displays. root can be a DisplayElement or a condition.
    def __init__(self, display_driver, font_loader, root = None):        
        self._font_loader = font_loader
        self._display_driver = display_driver

        self._display_tree = None
        self._root = root
       
    @property
    def bounds(self):
        return DisplayBounds(0, 0, self._display_driver.width, self._display_driver.height)

    # Initialize the GUI. Mus be called before usage, but after defining the contents.
    def init(self, appl):
        if not self._root:
            raise Exception() #"UiController has nothing to initialize")
        
        self._appl = appl

        self._display_tree = ConditionTree(
            subject = self._root,
            listener = self,
            allow_lists = False
        )
        self._root = None

        self._display_tree.init(appl)

        # Add elements which are Updateables to the update queue
        for root_element in self._display_tree.entries:
            root_element.make_splash(self._font_loader)

            updateable_elements = [i for i in root_element.contents_flat() if isinstance(i, Updateable)]
            
            for element in updateable_elements:
                appl.add_updateable(element)

        self._current_splash = None

    # Sets a new root element (can be conditional). Must be called before init().
    def set_root(self, root):
        if self._display_tree:
            raise Exception() #"UiController already initialized")
        
        self._root = root

    # Update display when condition(s) have changed
    def condition_changed(self, condition):
        if not self._appl.running:
            return
                
        # Show (potentially different) splash
        self.show()

    @property
    def current(self):
        return self._display_tree.value

    # Shows the current splash
    def show(self):
        if not self._display_tree:
            raise Exception() #"UiController not initialized")
        
        # Initialize all uninitialized splash roots
        for root_element in self._display_tree.entries:
            if not root_element.initialized():
                root_element.init(root_element, self._appl)

        root_element = self.current

        if root_element == self._current_splash:
            return
        
        self._current_splash = root_element
        self._display_driver.tft.show(root_element.splash)

    # Search an element by definition in all possible splashes
    def search(self, id, index = None):
        if not self._display_tree:
            raise Exception() #"UiController not initialized")
        
        for root_element in self._display_tree.entries:
            result = root_element.search(id, index)
            if result:                
                return result
            
        return None                

    # Creates a label
    def create_label(self, bounds = DisplayBounds(), layout = None, name = "", id = 0):
        return DisplayLabel(
            bounds = bounds,
            layout = layout,
            name = name,
            id = id if id else name
        )
    