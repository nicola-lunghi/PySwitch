import board

from ..Tools import Tools
from ..hardware.LedDriver import LedDriver
from ..model.FootSwitch import FootSwitch

from ...definitions import Actions, ActionEvents, Colors


# Main application class for Explore Mode
class ExploreModeController:
    def __init__(self, config):
        self.config = config

        print("+------------------+")
        print("|   EXPLORE MODE   |")
        print("+------------------+")
        print("")

        available_ports = self._get_available_ports()

        # NeoPixel driver, initialized to the maximum possible LEDs
        self.led_driver = LedDriver(
            self.config["neoPixelPort"], 
            len(available_ports) * FootSwitch.NUM_PIXELS
        )

        ports_assigned = self._init_switches(available_ports)

        if Tools.get_option(self.config, "debug") == True:
            print("Listening to: ")
            print(ports_assigned)        
            print("")

        self._currently_shown_switch_index = -1


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
                if Tools.get_option(self.config, "debug") == True:
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
                    "pixels": self._calculate_pixels(index)
                },
                "actions": [
                    {
                        "type": Actions.PRINT,
                        "events": [
                            ActionEvents.SWITCH_DOWN
                        ],
                        "text": "---------------------------------"
                    },
                    {
                        "type": Actions.EXPLORE_IO,
                        "events": [
                            ActionEvents.SWITCH_DOWN
                        ],
                        "name": port_def["name"]
                    },
                    {
                        "type": Actions.EXPLORE_PIXELS,
                        "events": [
                            ActionEvents.SWITCH_DOWN
                        ],
                        "step": scan_step
                    }
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
        return port_def["name_short"]

    # Determine pixel addressing for a switch index, assuming they are linear
    def _calculate_pixels(self, index):
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

    # Enlightens the next switch according to the passed step value. 
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
    
    # On a switch instance, set the color indicating whether it switches up or down
    def _indicate_action_color(self, switch):
        for action_config in switch.config["actions"]:
            if action_config["type"] != Actions.EXPLORE_PIXELS:
                continue

            if action_config["step"] > 0:
                switch.color = Colors.GREEN
                switch.brightness = 0.05

            elif action_config["step"] < 0:
                switch.color = Colors.ORANGE
                switch.brightness = 0.05

            else:
                switch.brightness = 0

            return

