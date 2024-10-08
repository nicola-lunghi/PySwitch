from usb_midi import ports
from adafruit_midi import MIDI

from .FootSwitchController import FootSwitchController
from .measurements import RuntimeMeasurement
from .actions.Action import Action
from .Client import Client, ClientRequestListener
from ..misc import Tools, Updateable, Updater, Memory


# Main application class (controls the processing)    
class Controller(ClientRequestListener, Updater):

    # IDs for all available measurements (for statistics)
    STAT_ID_TICK_TIME = "Tick"             # Time one processing loop takes overall
    STAT_ID_SWITCH_UPDATE_TIME = "SwUp"    # Time between switch state updates. This measurement costs a lot of overhead!

    # config:   Configuration dictionary. Must at least contain a "valueProvider" (instance of ClientValueProvider)
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
    # displays: list of DisplayElements to show on the TFT
    def __init__(self, led_driver, config, switches = [], displays = [], ui = None):
        Updater.__init__(self)

        # User interface
        self.ui = ui

        # Global config
        self.config = config

        # Switch config
        self._switch_definitions = switches

        # Statistical measurements (added by the displays etc.)
        self._measurements_tick_time = []
        self._measurements_switch_update = []

        # NeoPixel driver 
        self.led_driver = led_driver
        self.led_driver.init(self._get_num_pixels())
        
        # Parse some options
        self._midiChannel = Tools.get_option(self.config, "midiChannel", 1)                                  # MIDI channel to use
        self._midi_buffer_size = Tools.get_option(self.config, "midiBufferSize", 60)                        # MIDI buffer size
        self._max_consecutive_midi_msgs = Tools.get_option(self.config, "maxConsecutiveMidiMessages", 10)   # Max. number of MIDI messages being parsed before the next switch state evaluation

        self._debug = Tools.get_option(self.config, "debug", False)
        self._debug_ui_structure = Tools.get_option(self.config, "debugUserInterfaceStructure", False)        

        # Periodic update handler (the client is only asked when a certain time has passed)
        self.period = PeriodCounter(Tools.get_option(self.config, "updateInterval", 200))        

        # Set up the screen elements
        self._prepare_ui(displays)

        # Start MIDI communication
        self._init_midi()

        # Client adapter to send and receive parameters
        self.client = Client(self._midi, self.config)

        # Set up switches
        self.switches = []
        self._init_switches()

        if self._debug:
            Tools.print("Updateable queue length: " + repr(len(self.updateables)))

    # Creates the display areas
    def _prepare_ui(self, displays):
        for element in displays:
            element.debug = Tools.get_option(self.config, "debugDisplay")

            self.ui.root.add(element)

            if isinstance(element, Updateable):
                self.add_updateable(element)

    # Initialize switches
    def _init_switches(self):
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

    # Start MIDI communication and return the handler
    def _init_midi(self):
        if self._debug:
            Tools.print("-> Init MIDI")

        self._midi = MIDI(
            midi_out    = ports[1],
            out_channel = self._midiChannel - 1,
            midi_in     = ports[0],
            in_buf_size = self._midi_buffer_size, 
            debug       = Tools.get_option(self.config, "debugMidi")
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

        if measurement.type == self.STAT_ID_TICK_TIME:        
            self._measurements_tick_time.append(measurement)
            self.add_updateable(measurement)
            
        elif measurement.type == self.STAT_ID_SWITCH_UPDATE_TIME:
            self._measurements_switch_update.append(measurement)
            self.add_updateable(measurement)
        
        else:
            raise Exception("Runtime measurement type " + repr(measurement.type) + " not supported")

    # Runs the processing loop (which never ends)
    def process(self):
        if self._debug:
            Tools.print("-> Init UI:")            

        if self._debug_ui_structure:
            self.ui.root.print_debug_info(3)

        # Show user interface        
        self.ui.show(self)

        Memory.watch("Controller: Show UI")

        if self._debug:
            Tools.print("-> Done initializing, starting processing loop")

        # Start processing loop
        while True:
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

    # Process switches between the actions to really catch all events despite a long update run time, 
    # for example when the config has very many switches
    def process_pre_update(self, updateable):
        self._process_switches()

    # Detects switch changes
    def _process_switches(self):
        # This calls the start/finish methods on the statistics in reverse order to measure the time 
        # between switch updates        
        for m in self._measurements_switch_update:
            m.finish()

        # Update switch states
        for switch in self.switches:
            switch.process()

        for m in self._measurements_switch_update:
            m.start()

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
    def reset_display_areas(self):
        pass
        #if self._debug:
        #    Tools.print("-> Reset display areas")

        #self._info_parameters.reset()


###############################################################################################################


# Periodic update helper    
class PeriodCounter:
    def __init__(self, interval_millis):
        self._interval_millis = int(interval_millis)

        self._last_reset = 0

    @property
    def interval(self):
        return self._interval_millis

    # Returns if the period has been exceeded. If yes, it lso resets
    # the period to the current time.
    @property
    def exceeded(self):
        current_time = Tools.get_current_millis()
        if self._last_reset + self._interval_millis < current_time:
            self._last_reset = current_time
            return True
        return False
            
