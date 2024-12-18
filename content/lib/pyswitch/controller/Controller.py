from gc import collect, mem_free

from .FootSwitchController import FootSwitchController
from .actions import Action
from .Client import Client, BidirectionalClient
from ..misc import Updater, PeriodCounter, get_option, do_print, format_size, fill_up_to
from ..stats import Memory #, RuntimeStatistics


# Main application class (controls the processing)    
class Controller(Updater): #ClientRequestListener

    # IDs for all available measurements (for statistics)
    STAT_ID_TICK_TIME = 1             # Time one processing loop takes overall

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
    def __init__(self, led_driver, midi, protocol = None, config = {}, switches = [], ui = None, period_counter = None):
        Updater.__init__(self)

        # Flag which is used by display elements to show the user there is not enough memory left
        self.low_memory_warning = False

        # MIDI handler
        self.__midi = midi

        # User interface
        self.ui = ui        

        # Global config
        self.config = config
        update_interval = get_option(config, "updateInterval", 200)

        # Max. number of MIDI messages being parsed before the next switch state evaluation
        self.__max_consecutive_midi_msgs = get_option(config, "maxConsecutiveMidiMessages", 10)   

        # Print debug info        
        self.__debug_stats = get_option(config, "debugStats", False)        

        # Statistical measurement for tick time
        if self.__debug_stats:
            from .RuntimeMeasurement import RuntimeMeasurement

            self.__measurement_tick_time = RuntimeMeasurement(get_option(config, "debugStatsInterval", update_interval))
            self.__measurement_tick_time.add_listener(self)
            self.add_updateable(self.__measurement_tick_time)            

        # Limit of minimum free memory before low_memory_warning is set to True (the check is done before ticks
        # are running so this should be enough to operate all configurations imaginable. Normally you need about 
        # 10-15k from there, so 25k is enough headroom)
        self.__memory_warn_limit = get_option(config, "memoryWarnLimitBytes", 1024 * 15)  # 15kB

        # Clear MIDI buffers on startup
        self.__clear_buffer = get_option(config, "clearBuffers", True)

        # NeoPixel driver 
        self.led_driver = led_driver
        self.led_driver.init(self.__get_num_pixels(switches))
        
        # Periodic update handler (the client is only asked when a certain time has passed)
        self.period = period_counter
        if not self.period:
            self.period = PeriodCounter(update_interval)        

        # Initialize client access.
        self.__init_client(config, protocol)

        # Set up the screen elements
        if self.ui:
            self.ui.init(self)
            self.add_updateable(ui)

        # Set up switches
        self.__init_switches(switches)

    # Client access. When no protocol is passed, every value will be requested periodically. If a protocol
    # is passed, bidirectional communication is used according to the protocol.
    def __init_client(self, config, protocol):
        if protocol:
            self.client = BidirectionalClient(self.__midi, config, protocol)
            self.add_updateable(self.client)
        else:
            self.client = Client(self.__midi, config)

    # Initialize switches
    def __init_switches(self, switches):
        self.switches = []

        for sw_def in switches:
            switch = FootSwitchController(
                self,
                sw_def
            )

            self.switches.append(
                switch
            )

    # Runs the processing loop (which never ends)
    def process(self):
        # Show user interface
        if self.ui:            
            Memory.watch("Showing UI")

            self.ui.show()           
        
        Memory.watch("Application loaded")

        # Check memory usage and issue a warning if too high
        self._check_memory()

        # Consume all MIDI messages which might be still in some buffers, 
        # and start when the queue is empty.
        if self.__clear_buffer:
            self.__clear_midi_buffer()

        # Start processing loop
        while self.tick():
            pass

    # Single tick in the processing loop. Must return True to keep the loop alive.
    def tick(self):
        # If enabled, remember the tick starting time for statistics
        if self.__debug_stats:
            self.__measurement_tick_time.start()       

        # Update all Updateables in periodic intervals, less frequently than every tick.        
        if self.period.exceeded:
            self.update()

            Memory.watch("Controller: update", only_if_changed = True)

        # Receive all available MIDI messages
        self.__receive_midi_messages()

        # Output statistical info if enabled
        if self.__debug_stats:
            self.__measurement_tick_time.finish()        

        return True

    # We do not use the default Updater implementation to check for MIDI messages in between.
    def update(self):
        for u in self.updateables:
            # Receive MIDI messages in between updates, too
            self.__receive_midi_messages()

            u.update()

    # Receive MIDI messages, and in between check for switch state changes
    def __receive_midi_messages(self):
        #self._measurement_midi_jitter.finish()
        cnt = 0
        client = self.client
        max_msgs = self.__max_consecutive_midi_msgs

        while True:
            # Detect switch state changes
            self.__process_switches()

            #collect()
            midimsg = self.__midi.receive()

            # Process the midi message
            client.receive(midimsg)

            cnt = cnt + 1
            if not midimsg or cnt > max_msgs:
                break  

        #self._measurement_midi_jitter.start()

    # Detects switch changes
    #@RuntimeStatistics.measure
    def __process_switches(self):
        #self.__measurement_switch_jitter.finish()

        # Update switch states
        for switch in self.switches:
            switch.process()

        #self.__measurement_switch_jitter.start()

    # Returns how many NeoPixels are needed overall
    def __get_num_pixels(self, switches):
        ret = 0
        for sw_def in switches:
            pixels = get_option(sw_def["assignment"], "pixels", [])
            for p in pixels:
                pp1 = p + 1
                if pp1 > ret:
                    ret = pp1
        return ret

    # Consume all MIDI messages which might be still in some buffers.
    def __clear_midi_buffer(self):
        #cnt = 0
        while True:
            midimsg = self.__midi.receive()
            if not midimsg:
                #do_print("Cleared MIDI Buffer (" + repr(cnt) + " messages)")
                break
            #cnt += 1

    # Check if enough memory is left and set the warning flag if not.
    # This flag is used by display elements to warn the user.
    def _check_memory(self):
        collect()
        free_bytes = mem_free()
        
        if free_bytes < self.__memory_warn_limit:
            do_print("WARNING: Low Memory: " + format_size(free_bytes))
            
            self.low_memory_warning = True

    # Resets all switches
    def reset_switches(self, ignore_switches_list = []):
        for action in self.updateables:
            if not isinstance(action, Action):
                continue

            if action.switch in ignore_switches_list:
                continue

            action.reset()

    # Callback called when the measurement wants to show something
    def measurement_updated(self, measurement):
        collect()
        do_print(fill_up_to(str(measurement.name), 30, '.') + ": Max " + repr(measurement.value) + "ms, Avg " + repr(measurement.average) + "ms, Calls: " + repr(measurement.calls) + ", Free: " + format_size(mem_free()))

