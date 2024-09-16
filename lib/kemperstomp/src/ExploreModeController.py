import board

from .Tools import Tools
from .hardware.LedDriver import LedDriver
from .model.FootSwitch import FootSwitch

from ..kemperstomp_config import Config
from ..kemperstomp_def import Actions, Colors


# Main application class for Explore Mode
class ExploreModeController:
    def __init__(self):
        print("+------------------+")
        print("|   EXPLORE MODE   |")
        print("+------------------+")
        print("")

        available_ports = self._get_available_ports()

        # NeoPixel driver, initialized to the maximum possible LEDs
        self.led_driver = LedDriver(
            Config["neoPixelPort"], 
            len(available_ports) * FootSwitch.NUM_PIXELS
        )

        switches = self._init_switches(available_ports)

        if Tools.get_option(Config, "debug") == True:
            print("Listening to: ")
            print(switches)        
            print("")

        self.currently_shown_switch_index = -1


    # Initialize switches. Returns a list of port names initialized
    def _init_switches(self, available_ports):
        self.switches = []

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
                pass

            except Exception as ex:
                if Tools.get_option(Config, "debug") == True:
                    print("Error assigning port " + port_def["name"] + ":")
                    print(ex)

        return ret

    # Initializes a explore port switch. Returns the short ID of the port
    def _init_switch(self, port_def, index):
        if index % 2 == 0:
            scan_step = 1
        else:
            scan_step = -1

        switch = FootSwitch(
            self,
            {
                "assignment": {
                    "port": port_def["port"],
                    "pixels": self._get_pixels(index)
                },
                "actions": [
                    {
                        "type": Actions.PRINT,
                        "text": "---------------------------------"
                    },
                    {
                        "type": Actions.EXPLORE_IO,
                        "name": port_def["name"]
                    },
                    {
                        "type": Actions.EXPLORE_PIXELS,
                        "step": scan_step
                    }
                ],
                "initialColors": [
                    Colors.WHITE,
                    Colors.WHITE,
                    Colors.WHITE
                ],
                "initialBrightness": 0,
                "index": index              # This is a custom attribute not parsed by FootSwitch, but used internally in this class
            }
        )

        self.switches.append(switch)
        return port_def["name_short"]

    # Get pixel addressing for a switch index
    def _get_pixels(self, index):
        i = index * FootSwitch.NUM_PIXELS
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
                "name": "board." + name,
                "name_short": name,
                "port": getattr(board, name)
            })

        return ret

    # Runs the processing loop (which never ends)
    def process(self):
        print("Press switches...")
        print("")

        # Start processing loop
        while True:
            self._tick()

    # Processing loop implementation
    def _tick(self):
        # Process all switches
        for switch in self.switches:
            switch.process(None)

    # Enlightens the next switch in round robin. Returns the pixels list of the switch enlightened.
    def show_next_switch(self, step):
        self.currently_shown_switch_index = self.currently_shown_switch_index + step
        
        if self.currently_shown_switch_index >= len(self.switches):
            self.currently_shown_switch_index = 0
        
        if self.currently_shown_switch_index < 0:
            self.currently_shown_switch_index = len(self.switches) - 1

        ret = None
        for switch in self.switches:
            if switch.config["index"] == self.currently_shown_switch_index:
                switch.set_brightness(1)
                ret = switch.config["assignment"]["pixels"]
            else:
                switch.set_brightness(0)

        return ret