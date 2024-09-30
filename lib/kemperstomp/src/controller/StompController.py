import usb_midi
import adafruit_midi 

from .FootSwitchController import FootSwitchController
from .Statistics import Statistics, StatisticsListener
from .PeriodCounter import PeriodCounter
from .Conditions import Conditions
from .InfoDisplays import InfoDisplays
from ..client.Client import Client
from ..client.ClientRequest import ClientRequestListener
from ..misc.Tools import Tools
from ...definitions import ProcessingConfig, FootSwitchDefaults
from ...display import DisplayAreas, DisplayAreaDefinitions


# Main application class (controls the processing)    
class StompController(ClientRequestListener, StatisticsListener):
    def __init__(self, ui, led_driver, config):
        self.ui = ui
        self.config = config

        # NeoPixel driver 
        self.led_driver = led_driver
        self.led_driver.init(len(self.config["switches"]) * FootSwitchDefaults.NUM_PIXELS)
        
        self._midiChannel = self.config["midiChannel"]                            # MIDI channel to use
        self._midi_buffer_size = self.config["midiBufferSize"]                    # MIDI buffer size (default: 60)
        self._show_stats = Tools.get_option(self.config, "showFrameStats", False) # Show frame statistics
        self._debug = Tools.get_option(self.config, "debug", False)
        self._debug_ui_structure = Tools.get_option(self.config, "debugUserInterfaceStructure", False)        

        # Periodic update handler (the client is only asked when a certain time has passed)
        self._period = PeriodCounter(self.config["updateInterval"])

        # Conditions handler
        self.conditions = Conditions()

        # Set up the screen elements
        self._prepare_ui()

        # Controller for the display areas
        self._info_parameters = InfoDisplays(
            self,
            Tools.get_option(self.config, "displays", []),
            Tools.get_option(self.config, "debugParameters", False)
        )

        # Statistics instance (only used when switched on or a Performance Indicator is defined)       
        self.statistics = None
        if self._show_stats == True or self.ui.root.search({ "id": DisplayAreas.PERFORMANCE_INDICATOR }) != None:
            self.statistics = Statistics(Tools.get_option(self.config, "statsIntervalMillis", 200))
            self.statistics.add_listener(self)
            self.statistics_display = self.ui.root.search({ "id": DisplayAreas.STATISTICS })

        # MIDI communication
        self._init_midi()

        # Client adapter to send and receive parameters
        self.client = Client(self._midi, self.config)

        # Set up switches
        self.switches = []
        self._init_switches()

    # Creates the display areas
    def _prepare_ui(self):
        for element in DisplayAreaDefinitions:
            if element.id == DisplayAreas.STATISTICS and self._show_stats != True:
                continue

            element.debug = Tools.get_option(self.config, "debugDisplay")

            self.ui.root.add(element)

    # Initialize switches
    def _init_switches(self):
        if self._debug == True:
            Tools.print("-> Init switches")
                    
        for swDef in self.config["switches"]:
            self.switches.append(
                FootSwitchController(
                    self,
                    swDef
                )
            )

    # Start MIDI communication and return the handler
    def _init_midi(self):
        if self._debug == True:
            Tools.print("-> Init MIDI")

        self._midi = adafruit_midi.MIDI(
            midi_out    = usb_midi.ports[1],
            out_channel = self._midiChannel - 1,
            midi_in     = usb_midi.ports[0],
            in_buf_size = self._midi_buffer_size, 
            debug       = Tools.get_option(self.config, "debugMidi")
        )

    # Runs the processing loop (which never ends)
    def process(self):
        if self._debug == True:
            Tools.print("-> Init UI:")            

        # Show user interface        
        self.ui.show(self)

        if self._debug_ui_structure == True:
            self.ui.root.print_debug_info(3)

        if self._debug == True:
            Tools.print("-> Done initializing, starting processing loop")

        # Start processing loop
        while True:
            # If enabled, remember the tick starting time for statistics
            if self.statistics != None:
                self.statistics.start()

            # Receive all available MIDI messages            
            cnt = 0
            while True:
                midimsg = self._midi.receive()

                # Process the midi message
                self.client.receive(midimsg)

                cnt = cnt + 1
                if midimsg == None or cnt > ProcessingConfig.MAX_NUM_CONSECUTIVE_MIDI_MESSAGES:
                    break            
        
            # Process all switches 
            for switch in self.switches:
                switch.process()
            
            # Update client parameters in periodic intervals, less frequently then every tick
            if self._period.exceeded == True:
                self._update()

            # Output statistical info if enabled
            if self.statistics != None:
                self.statistics.finish()

    # Update (called on every periodic update interval)
    def _update(self):
        # Update conditions
        self.conditions.update()

        # Update displayed parameters
        self._info_parameters.update()

        # Update switch actions
        for switch in self.switches:
            switch.update()

    # Resets all switches
    def reset_switches(self, ignore_switches_list = []):
        if self._debug == True:
            Tools.print("-> Reset switches, ignoring " + repr(ignore_switches_list))

        for switch in self.switches:
            if not switch in ignore_switches_list:
                switch.reset()

    # Resets all display areas
    def reset_display_areas(self):
        if self._debug == True:
            Tools.print("-> Reset display areas")

        self._info_parameters.reset()

    # Update stats label message
    def update_statistics(self, statistics):        
        if self.statistics_display != None:
            self.statistics_display.text = statistics.get_message()
