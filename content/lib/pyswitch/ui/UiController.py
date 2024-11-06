from .ui import DisplayBounds, DisplaySplash
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
            raise Exception("UiController has nothing to initialize")
        
        self._appl = appl

        self._display_tree = ConditionTree(
            subject = self._root,
            listener = self,
            replacer = self,
            allow_lists = False
        )
        self._root = None

        self._display_tree.init(appl)

        # Add elements which are Updateables to the update queue
        for splash in self._display_tree.entries:
            updateable_elements = [i for i in splash.root.contents_flat() if isinstance(i, Updateable)]
            
            for element in updateable_elements:
                appl.add_updateable(element)

        self._current_splash = None

    # Sets a new root element (can be conditional). Must be called before init().
    def set_root(self, root):
        if self._display_tree:
            raise Exception("UiController already initialized")
        
        self._root = root

    # Replacer for ConditionTree: Create Splash handler from the element passed
    def replace(self, element):
        return DisplaySplash(element, self._font_loader)

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
            raise Exception("UiController not initialized")
        
        # Initialize all uninitialized splash roots
        for splash_container in self._display_tree.entries:
            if not splash_container.root.initialized():
                splash_container.root.init(splash_container, self._appl)

        splash_container = self.current

        if splash_container == self._current_splash:
            return
        
        self._current_splash = splash_container
        self._display_driver.tft.show(splash_container.splash)

    # Search an element by definition in all possible splashes
    def search(self, definition):
        if not self._display_tree:
            raise Exception("UiController not initialized")
        
        for splash_container in self._display_tree.entries:
            result = splash_container.root.search(definition)
            if result:                
                return result
            
        return None                

    # Creates a label
    def create_label(self, bounds = DisplayBounds(), layout = {}, name = "", id = 0):
        return DisplayLabel(
            bounds = bounds,
            layout = layout,
            name = name,
            id = id if id else name
        )
    