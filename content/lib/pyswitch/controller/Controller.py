from gc import collect, mem_free

from .FootSwitchController import FootSwitchController
from .RuntimeMeasurement import RuntimeMeasurement
from .actions.Action import Action
from .Client import Client, BidirectionalClient
from ..misc import Updater, PeriodCounter, get_option, do_print, format_size
from ..Memory import Memory


# Main application class (controls the processing)    
class Controller(Updater): #ClientRequestListener

    # IDs for all available measurements (for statistics)
    STAT_ID_TICK_TIME = 1             # Time one processing loop takes overall
    #STAT_ID_SWITCH_UPDATE_TIME = 2    # Time between switch state updates. This measurement costs a lot of overhead!

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
    def __init__(self, led_driver, communication, midi, config = {}, switches = [], ui = None, period_counter = None):
        Updater.__init__(self)

        self.running = False
        self.low_memory_warning = False

        self._midi = midi

        # User interface
        self.ui = ui

        # Global config
        self.config = config
        update_interval = get_option(config, "updateInterval", 200)

        # Max. number of MIDI messages being parsed before the next switch state evaluation
        self._max_consecutive_midi_msgs = get_option(config, "maxConsecutiveMidiMessages", 10)   

        # Statistical measurements (added by the displays etc.)
        self._measurement_tick_time = RuntimeMeasurement(interval_millis = get_option(config, "debugStatsInterval", update_interval))
        self._measurement_tick_time.add_listener(self)
        self._memory_warn_limit = get_option(config, "memoryWarnLimitBytes", 1024 * 15)  # 15kB

        #self._measurement_switch_update = RuntimeMeasurement(interval_millis = get_option(config, "debugStatsInterval", update_interval))
        #self._measurement_switch_update.add_listener(self)

        # Print debug info        
        self._debug_stats = get_option(config, "debugStats", False)        

        # Clear MIDI buffers on startup
        self._clear_buffers = get_option(config, "clearBuffers", False)

        # NeoPixel driver 
        self.led_driver = led_driver
        self.led_driver.init(self._get_num_pixels(switches))
        
        # Periodic update handler (the client is only asked when a certain time has passed)
        self.period = period_counter
        if not self.period:
            self.period = PeriodCounter(update_interval)        

        # Client adapter to send and receive parameters
        value_provider = communication["valueProvider"]

        # Bidirectional MIDI Protocol (optional)
        protocol = get_option(communication, "protocol", None)
        if protocol:
            self.client = BidirectionalClient(self._midi, config, value_provider, protocol)
            self.add_updateable(self.client)
        else:
            self.client = Client(self._midi, config, value_provider)

        # Set up the screen elements
        if self.ui:
            self.ui.init(self)

        # Set up switches
        self._init_switches(switches)

    # Initialize switches
    def _init_switches(self, switches):
        self.switches = []

        for sw_def in switches:
            switch = FootSwitchController(
                self,
                sw_def
            )

            self.switches.append(
                switch
            )

    # Returns how many NeoPixels are needed overall
    def _get_num_pixels(self, switches):
        ret = 0
        for sw_def in switches:
            pixels = get_option(sw_def["assignment"], "pixels", [])
            for p in pixels:
                pp1 = p + 1
                if pp1 > ret:
                    ret = pp1
        return ret

    # Runs the processing loop (which never ends)
    def process(self):
        # Show user interface
        if self.ui:            
            Memory.watch("Showing UI")

            self.ui.show()           
        
        self.running = True

        Memory.watch("Application loaded")

        # Check memory usage and issue a warning if too high
        collect()
        free_bytes = mem_free()
        if free_bytes < self._memory_warn_limit:
            do_print("WARNING: Low Memory: " + format_size(free_bytes))
            self.low_memory_warning = True
        del free_bytes

        # For debugging only: Empty buffer. This is only needed when 
        # developing using MIDI routing between the device and client, 
        # which may have buffering.
        if self._clear_buffers:
            cnt = 0
            while True:
                midimsg = self._midi.receive()
                if not midimsg:
                    print("Cleared MIDI Buffer (" + repr(cnt) + " messages)")
                    break
                cnt += 1
            del cnt

        # Start processing loop
        while self.tick():
            pass

    # Single tick in the processing loop. Must return True to keep the loop alive.
    def tick(self):
        # If enabled, remember the tick starting time for statistics
        self._measurement_tick_time.start()       

        # Update all Updateables in periodic intervals, less frequently then every tick
        if self.period.exceeded:
            self.update()

            Memory.watch("Controller: update", only_if_changed = True)

            # Update tick time measurement
            self._measurement_tick_time.update()

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
        self._measurement_tick_time.finish()        

        return True

    # Detects switch changes
    def _process_switches(self):
        # This calls the start/finish methods on the statistics in reverse order to measure the time 
        # between switch updates        
        #self._measurement_switch_update.finish()

        # Update switch states
        for switch in self.switches:
            switch.process()

        #self._measurement_switch_update.start()

    # Resets all switches
    def reset_switches(self, ignore_switches_list = []):
        for action in self.updateables:
            if not isinstance(action, Action):
                continue

            if action.switch in ignore_switches_list:
                continue

            action.reset()

    # Resets all display areas
    def reset_display_areas(self):   # pragma: no cover
        pass

        #self._info_parameters.reset()

    def get_measurement(self, id):
        if id == self.STAT_ID_TICK_TIME:
            return self._measurement_tick_time

    def measurement_updated(self, measurement):
        if not self._debug_stats: 
            return
        
        collect()
        
        do_print("Max " + str(measurement.value) + "ms, Avg " + str(measurement.average) + "ms, Free: " + format_size(mem_free()))
