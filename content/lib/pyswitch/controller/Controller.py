from .MidiController import MidiController
from .FootSwitchController import FootSwitchController
from .measurements import RuntimeMeasurement
from .actions.Action import Action
from .Client import Client, BidirectionalClient
from ..misc import Tools, Updater, PeriodCounter
from ..Memory import Memory


# Main application class (controls the processing)    
class Controller(Updater): #ClientRequestListener

    # IDs for all available measurements (for statistics)
    _STAT_ID_TICK_TIME = 1             # Time one processing loop takes overall
    _STAT_ID_SWITCH_UPDATE_TIME = 2    # Time between switch state updates. This measurement costs a lot of overhead!

    # config:   Configuration dictionary. 
    # switches: [           list of switch definitions
    #                {
    #                     "assignment": {   Selects which switch of your device you want to assign. 
    #                          "model":    Instance of AdafruitSwitch
    #                          "pixels":   Optional, tiple of LED indices to assign to the switch, for example (0, 1, 2) 
    #                          "name":     Optional, name of the switch for output
    #                     },
    #
    #                     # Defines the actions you want to happen on different events of the switch. You can 
    #                     # define as many actions as you want, they will be executed in that order.
    #                     # You can also use the Condition class to have different actions active depending
    #                     # on another parameter.
    #                     "actions": [
    #                           ...See Actions.py and its children
    #                     ]
    #                },
    #                ...
    #           ]
    # value_provider: Value provider for the client
    # displays: list of DisplayElements to show on the TFT
    def __init__(self, led_driver, communication, midi, config = {}, switches = [], ui = None, period_counter = None):
        Updater.__init__(self)

        self.running = False

        self._midi = midi

        # User interface
        self.ui = ui

        # Global config
        self.config = config

        self._max_consecutive_midi_msgs = Tools.get_option(self.config, "maxConsecutiveMidiMessages", 10)   # Max. number of MIDI messages being parsed before the next switch state evaluation
        self._debug = Tools.get_option(self.config, "debug", False)
        #self._debug_ui_structure = Tools.get_option(self.config, "debugUserInterfaceStructure", False)        

        # Switch config
        self._switch_definitions = switches

        # Statistical measurements (added by the displays etc.)
        self._measurements_tick_time = []
        #self._measurements_switch_update = []

        # NeoPixel driver 
        self.led_driver = led_driver
        self.led_driver.init(self._get_num_pixels())
        
        # Periodic update handler (the client is only asked when a certain time has passed)
        self.period = period_counter
        if not self.period:
            self.period = PeriodCounter(Tools.get_option(self.config, "updateInterval", 200))        

        # Client adapter to send and receive parameters
        value_provider = communication["valueProvider"]

        # Bidirectional MIDI Protocol (optional)
        protocol = Tools.get_option(communication, "protocol", None)
        if protocol:
            self.client = BidirectionalClient(self._midi, self.config, value_provider, protocol)
            self.add_updateable(self.client)
        else:
            self.client = Client(self._midi, self.config, value_provider)

        # Set up the screen elements
        if self.ui:
            self.ui.init(self)

        # Set up switches
        self._init_switches()

        if self._debug:
            Tools.print("Updateable queue length: " + repr(len(self.updateables)))    

    # Initialize switches
    def _init_switches(self):
        self.switches = []

        if self._debug:
            Tools.print("-> Init switches")
                    
        for sw_def in self._switch_definitions:
            switch = FootSwitchController(
                self,
                sw_def
            )

            self.switches.append(
                switch
            )

    # Returns how many NeoPixels are needed overall
    def _get_num_pixels(self):
        ret = 0
        for sw_def in self._switch_definitions:
            pixels = Tools.get_option(sw_def["assignment"], "pixels", [])
            for p in pixels:
                pp1 = p + 1
                if pp1 > ret:
                    ret = pp1
        return ret

    # Adds a runtime measurement. 
    def add_runtime_measurement(self, measurement):
        if not isinstance(measurement, RuntimeMeasurement):
            return

        if measurement.type == self._STAT_ID_TICK_TIME:        
            self._measurements_tick_time.append(measurement)
            self.add_updateable(measurement)
            
        #elif measurement.type == self._STAT_ID_SWITCH_UPDATE_TIME:
        #    self._measurements_switch_update.append(measurement)
        #    self.add_updateable(measurement)
        
        else:
            raise Exception("Runtime measurement type " + repr(measurement.type) + " not supported")

    # Runs the processing loop (which never ends)
    def process(self):
        # Show user interface
        if self.ui:            
            self.ui.show()

            Memory.watch("Controller: Showing UI")
        
        self.running = True

        if self._debug:
            Tools.print("-> Done initializing, starting processing loop")

        Memory.watch("Controller: Starting loop")

        # Start processing loop
        while self.tick():
            pass

    # Single tick in the processing loop. Must return True to keep the loop alive.
    def tick(self):
        #Memory.watch("Controller: tick")

        # If enabled, remember the tick starting time for statistics
        for m in self._measurements_tick_time:
            m.start()       

        # Update all Updateables in periodic intervals, less frequently then every tick
        if self.period.exceeded:
            self.update()

        # Receive all available MIDI messages            
        cnt = 0
        while True:
            # Detect switch state changes
            self._process_switches()

            midimsg = self._midi.receive()

            # Process the midi message
            self.client.receive(midimsg)

            cnt = cnt + 1
            if not midimsg or cnt > self._max_consecutive_midi_msgs:
                break  

        # Output statistical info if enabled
        for m in self._measurements_tick_time:
            m.finish()

        return True

    # Detects switch changes
    def _process_switches(self):
        # This calls the start/finish methods on the statistics in reverse order to measure the time 
        # between switch updates        
        #for m in self._measurements_switch_update:
        #    m.finish()

        # Update switch states
        for switch in self.switches:
            switch.process()

        #for m in self._measurements_switch_update:
        #    m.start()

    # Resets all switches
    def reset_switches(self, ignore_switches_list = []):
        if self._debug:  
            Tools.print("-> Reset switches, ignoring " + repr(ignore_switches_list))

        for action in self.updateables:
            if not isinstance(action, Action):
                continue

            if action.switch in ignore_switches_list:
                continue

            action.reset()

    # Resets all display areas
    def reset_display_areas(self):   # pragma: no cover
        pass
        #if self._debug:
        #    Tools.print("-> Reset display areas")

        #self._info_parameters.reset()


