import board

from ..misc import Updater, Colors
from .FootSwitchController import FootSwitchController
from .actions.Action import Action
from ..hardware.adafruit import AdafruitSwitch
from ..ui.elements.elements import DisplayLabel, DisplaySplitContainer


# Number of columns for port display
NUM_PORT_COLUMNS = 5   


# Action to explore switch GPIO assignments (used internally only in explore mode!)
# Also used to examine neopixel addressing.
class ExploreAction(Action):
    
    def __init__(self, config = {}):
        super().__init__(config)

        self._name = config["name"]
        self._step = config["step"]
           
    # Must be called before usage
    def init(self, appl, switch):
        self.appl = appl
        self.switch = switch

        self._label = self.appl.get_next_port_label()

        if self._label:
            self._label.text = self._name

    def push(self):
        pixel_out = self._trigger_pixel_search()
        print("board." + self._name + " " + pixel_out)

        if self.appl.ui:
            self.appl.pixel_display.text = pixel_out

        if self._label:
            self.appl.reset_port_markers()
            self._label.back_color = Colors.RED
            
    # Enlighten the next available switch LEDs and returns a report string.
    def _trigger_pixel_search(self):
        current = self.appl.show_next_switch(self._step)
        if current == None:
            return
        
        # Get output for pixel exploration
        num_switch_leds = len(self.appl.switches) * len(self.switch.pixels)
        return "Pixels: (" + repr(current[0]) + ", " + repr(current[1]) + ", " + repr(current[2]) + ") of " + repr(num_switch_leds)        


###########################################################################################################################


# Main application class for Explore Mode
class ExploreModeController(Updater):

    def __init__(self, led_driver, ui = None, num_pixels_per_switch = 3):
        Updater.__init__(self)

        self.ui = ui
        self.config = {}
        self._num_pixels_per_switch = num_pixels_per_switch
        self._currently_shown_switch_index = -1

        # Get list of available ports
        available_ports = self._get_available_ports()

        # NeoPixel driver, initialized to the maximum possible amount of LEDs
        self.led_driver = led_driver
        self.led_driver.init(len(available_ports) * self._num_pixels_per_switch)

        if self.ui:
            self._setup_ui()

            # Try to initialize all available ports. This gets us the list of ports successfully assigned.
            self._init_switches(available_ports)
        else:
            # Try to initialize all available ports. This gets us the list of ports successfully assigned.
            ports_assigned = self._init_switches(available_ports)

            print("+------------------+")
            print("|   EXPLORE MODE   |")
            print("+------------------+")
            print("")
            print("Listening to: ")
            print(self._get_ports_string(ports_assigned))            
            print("")

    # Set up user interface
    def _setup_ui(self):
        bounds = self.ui.root.bounds.clone()

        # Display for currently enlightened pixels
        self.pixel_display = DisplayLabel(
            bounds = bounds.remove_from_bottom(40),
            layout = {
                "font": "/fonts/A12.pcf",
                "backColor": Colors.DARK_GREEN
            }
        )
        self.ui.root.add(self.pixel_display)

        # Display for ports
        self._ports_display_rows = DisplaySplitContainer(
            bounds = bounds,
            direction = DisplaySplitContainer.VERTICAL
        )
        self.ui.root.add(self._ports_display_rows)

    # Runs the processing loop (which never ends)
    def process(self):
        # Show user interface        
        self.ui.show(self)

        # Start processing loop
        while True:
            # Update switch states
            for switch in self.switches:
                switch.process()

            # Update actions
            self.update()

    # Called by ExplorePixelAction: Enlightens the next switch according to the passed step value. 
    # Returns the pixels tuple of the switch currently enlightened.
    def show_next_switch(self, step):
        # Add step and regard bounds
        self._currently_shown_switch_index = self._currently_shown_switch_index + step
        
        if self._currently_shown_switch_index >= len(self.switches):
            self._currently_shown_switch_index = 0
        
        if self._currently_shown_switch_index < 0:
            self._currently_shown_switch_index = len(self.switches) - 1

        # Show the currently selected switch, and for all others, indicate
        # whether they increase or decrease.
        ret = None
        for switch in self.switches:
            if switch.config["index"] == self._currently_shown_switch_index:
                switch.color = Colors.WHITE
                switch.brightness = 1
                ret = switch.config["assignment"]["pixels"]
            else:
                self._indicate_action_color(switch)

        return ret
    
    # Returns a small representation of the ports passed
    def _get_ports_string(self, ports_assigned):
        return ", ".join([port for port in ports_assigned])

    # Initialize switches. Returns a list of port names initialized
    def _init_switches(self, available_ports):
        self.switches = []
        self._next_label_index = 0

        ret = []

        for port_def in available_ports:
            try:                                
                ret.append(
                    self._init_switch(
                        port_def,
                        len(ret)
                    )
                )

            except ValueError:
                # This is no error as not all pins can be assigned to switches
                pass

            except Exception as ex:
                print("Error assigning port " + port_def["name"] + ":")
                raise ex 

        return ret

    # Initializes a explore port switch. Returns the short ID of the port
    def _init_switch(self, port_def, index):
        if index % 2 == 0:
            scan_step = 1
        else:
            scan_step = -1

        switch = FootSwitchController(
            self,
            {
                "assignment": {
                    "model": AdafruitSwitch(port_def["port"]),
                    "pixels": self._calculate_pixels(index)
                },
                "actions": [
                    ExploreAction({
                        "name": port_def["name"],
                        "step": scan_step
                    })
                ],
                "initialColors": [
                    Colors.WHITE,
                    Colors.WHITE,
                    Colors.WHITE
                ],
                "initialBrightness": 0,
                "index": index              # This is a custom attribute not parsed by FootSwitch, but used internally in this class only
            }
        )

        self.switches.append(switch)
        return port_def["name"]

    # Returns the next available label (used by the ExploreAction)
    def get_next_port_label(self):
        if not self.ui:
            return None
        
        row = self._ports_display_rows.last_child
        if not row or len(row.children) >= NUM_PORT_COLUMNS:
            row = DisplaySplitContainer(
                direction = DisplaySplitContainer.HORIZONTAL
            )
            self._ports_display_rows.add(row)

        label = DisplayLabel(
            layout = {
                "font": "/fonts/A12.pcf",
                "backColor": Colors.BLACK,
                "stroke": 1
            }
        )

        row.add(label)

        return label

    # Resets all ports markers
    def reset_port_markers(self):
        for row in self._ports_display_rows.children:
            for col in row.children:
                col.back_color = Colors.DARK_BLUE

    # Determine pixel addressing for a switch index, assuming they are linear
    def _calculate_pixels(self, index):
        i = index * self._num_pixels_per_switch

        return (
            i, 
            i + 1, 
            i + 2
        )

    # Determines all available GP* ports
    def _get_available_ports(self):
        names = dir(board)
        ret = []
        for name in names:
            if not name.startswith("GP"):
                continue

            ret.append({
                "name": name,
                "port": getattr(board, name)
            })

        return ret
    
    # On a switch instance, set the color indicating whether it switches up or down
    def _indicate_action_color(self, switch):
        for action in switch.config["actions"]:
            step = action.config["step"]

            if step > 0:
                switch.color = Colors.GREEN
                switch.brightness = 0.01

            elif step < 0:
                switch.color = Colors.ORANGE
                switch.brightness = 0.01

            else:
                switch.brightness = 0

            return

