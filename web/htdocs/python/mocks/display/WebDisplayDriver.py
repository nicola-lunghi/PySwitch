#from browser import document
#from browser.html import CANVAS
#from browser import console
from js import document

class WebTFT:
    def __init__(self, width, height, dom_namespace):
        self.width = width
        self.height = height
        
        self.splash = None
        self.canvas = None

        self.dom_namespace = dom_namespace

    def show(self, splash):        
        self.splash = splash
        self.update()

    def update(self):
        id = self.dom_namespace + "-display"
        self.canvas = document.getElementById(id)
        if not self.canvas:
            raise Exception("No canvas found with ID " + repr(id))
        
        self.canvas.width = self.width
        self.canvas.height = self.height
        
        ctx = self.canvas.getContext('2d')
        ctx.fillStyle = "black"
        ctx.fillRect(
            0,
            0,
            self.width,
            self.height
        )

        for s in self.splash:
            s.render(self.canvas, 0, 0)


class WebDisplayDriver:
    def __init__(self,
                 width, 
                 height,
                 dom_namespace 
        ):
        self.tft = WebTFT(width, height, dom_namespace)
        
    # Initialize the display
    def init(self):        
        pass

    def update(self):
        self.tft.update()