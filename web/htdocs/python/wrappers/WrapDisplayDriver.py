from js import document

class WrapTFT:
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
        if not self.canvas:
            self.canvas = self.get_canvas(self.dom_namespace)            
        
        if not self.canvas:
            return
        
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

    @staticmethod
    def get_canvas(dom_namespace):
        id = dom_namespace + "-display"
        canvas = document.getElementById(id)
        # if not canvas:
        #     raise Exception("No canvas found with ID " + repr(id))
        return canvas


class WrapDisplayDriver:
    def __init__(self,
                 width, 
                 height,
                 dom_namespace 
        ):
        self.tft = WrapTFT(width, height, dom_namespace)
        
    # Initialize the display
    def init(self):        
        pass

    def update(self):
        self.tft.update()