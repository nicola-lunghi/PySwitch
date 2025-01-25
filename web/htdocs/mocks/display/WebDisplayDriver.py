from browser import document
from browser.html import CANVAS

class WebTFT:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        self.splash = None
        self.canvas = None

    def show(self, splash):
        content = document.select_one("#content")
        content.clear()

        self.canvas = CANVAS(
            width = self.width,
            height = self.height
        )

        content <= self.canvas

        ctx = self.canvas.getContext('2d')
        ctx.fillStyle = "black"
        ctx.fillRect(
            0,
            0,
            self.width,
            self.height
        )

        self.splash = splash
        self.update()

    def update(self):
        for s in self.splash:
            s.render(self.canvas, 0, 0)


class WebDisplayDriver:
    def __init__(self, 
                 width = 240, 
                 height = 240                
        ):
        self.tft = WebTFT(width, height)
        
    # Initialize the display
    def init(self):        
        pass