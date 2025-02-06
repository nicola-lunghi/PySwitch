from js import document
from pyodide.ffi.wrappers import add_event_listener

from pyswitch.hardware.adafruit.AdafruitSwitch import AdafruitSwitch

# Builds the DOM for the device visualization
class PySwitchDevice:

    def __init__(self, container_id, dom_namespace):        
        self.container = document.getElementById(container_id)
        if not self.container:
            raise Exception("Container element with ID " + container_id + " not found")
        
        self.dom_namespace = dom_namespace

    # Initialize to a given set of inputs and splashes
    def init(self, inputs, splashes):
        self.container.innerHTML = ""

        # Clear contents and create container
        self.__init_background()
        
        # Add display (canvas)
        self.__init_display()

        # Add switches and LEDs
        self.__init_switches(inputs)

    # Initialize background IMG
    def __init_background(self):
        img = document.createElement("img")
        img.id = self.dom_namespace + "-background"
        self.container.appendChild(img)

    # Initialize the display canvas
    def __init_display(self):
        canvas = document.createElement("canvas")
        canvas.id = self.dom_namespace + "-display"
        self.container.appendChild(canvas)

    # Creates DOM elements for all switches and LEDs. Expects the Inputs list from inputs.py.
    def __init_switches(self, inputs):
        # Create container for all inputs
        inputs_container = document.createElement("div")
        inputs_container.id = self.dom_namespace + "-inputs"
        self.container.appendChild(inputs_container)

        for input in inputs:
            # Decide from the model type which input has to be created
            model = input["assignment"]["model"]

            if isinstance(model, AdafruitSwitch):
                # Switch
                element = document.createElement("div")
                element.id = self.dom_namespace + "-switch-gp" + str(model._AdafruitSwitch__port)
                element.className = self.dom_namespace + "-switch"

                def on_click(event):
                    event.currentTarget.dataset.pushed = True

                def on_release(event):
                    event.currentTarget.dataset.pushed = False

                add_event_listener(element, "mousedown", on_click)
                add_event_listener(element, "touchstart", on_click)
                add_event_listener(element, "mouseup", on_release)
                add_event_listener(element, "mouseout", on_release)
                add_event_listener(element, "mouseleave", on_release)
                add_event_listener(element, "touchend", on_release)

                inputs_container.appendChild(element)

                visual_element = document.createElement("div")
                visual_element.className = self.dom_namespace + "-switch-visual"
                element.appendChild(visual_element)

                overlay_element = document.createElement("div")
                overlay_element.className = self.dom_namespace + "-switch-overlay"
                element.appendChild(overlay_element)

            else:
                # Unknown type
                print("Ignoring input (unsupported type: " + input.__class__.__name__ + ")")
                continue

            # LEDs (can be added to any type)
            if visual_element and "pixels" in input["assignment"]:
                pixels = input["assignment"]["pixels"]

                for pixel in pixels:
                    pixel_element = document.createElement("div")                
                    pixel_element.id = self.dom_namespace + "-led-" + str(pixel)
                    pixel_element.className = self.dom_namespace + "-led"

                    visual_element.appendChild(pixel_element)
                
