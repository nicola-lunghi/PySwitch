from .ui import DisplayBounds
from ..misc import Updateable, Updater


class UiController(Updater, Updateable):

    # Creates the displays. root can be a DisplayElement or a condition.
    def __init__(self, display_driver, font_loader, splash_callback):     
        Updater.__init__(self)

        self._font_loader = font_loader
        self._display_driver = display_driver
        self._splash_callback = splash_callback

        self._current_splash_element = None

    @property
    def bounds(self):
        return DisplayBounds(0, 0, self._display_driver.width, self._display_driver.height)

    # Initialize the GUI. Mus be called before usage.
    def init(self, appl):
        self._appl = appl

        self._splash_callback.init(appl, self)
        self.add_updateable(self._splash_callback)

    def parameter_changed(self, mapping):
        self.show()

    #@property
    #def current(self):
    #    return self._current_splash_element #self._display_tree.value

    # Shows the current splash
    def show(self):
        # Get DisplayElement from callback
        splash_element = self._splash_callback.get()

        if splash_element == self._current_splash_element:
            return

        # Make it a splash (creates the Group if not yet done)
        splash_element.make_splash(self._font_loader)

        if not splash_element.initialized():
            splash_element.init(splash_element, self._appl)

        # Add elements which are Updateables to the update queue
        self.updateables = [i for i in splash_element.contents_flat() if isinstance(i, Updateable)]
        self.add_updateable(self._splash_callback)
        
        # Show splash
        self._current_splash_element = splash_element
        self._display_driver.tft.show(splash_element.splash)
