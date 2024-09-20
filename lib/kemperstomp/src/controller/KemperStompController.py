import usb_midi
import adafruit_midi 

from .FootSwitch import FootSwitch
from .Statistics import Statistics
from .PeriodCounter import PeriodCounter
from ..hardware.LedDriver import LedDriver
from ..model.Kemper import Kemper
from ..model.KemperRequest import KemperRequestListener
from ..Tools import Tools
from ...mappings import KemperMappings
from ...definitions import KemperDefinitions, FootSwitchDefaults
from ...display import DisplayAreas, DisplayAreaDefinitions


# Main application class (controls the processing)    
class KemperStompController(KemperRequestListener):
    def __init__(self, ui, config):
        self.ui = ui
        self.config = config

        # NeoPixel driver 
        self.led_driver = LedDriver(self.config["neoPixelPort"], len(self.config["switches"]) * FootSwitchDefaults.NUM_PIXELS)    
        
        self._last_update = 0                                                     # Used to store the last update timestamp
        self._midiChannel = self.config["midiChannel"]                            # MIDI channel to use
        self._midi_buffer_size = self.config["midiBufferSize"]                    # MIDI buffer size (default: 60)
        self._show_stats = Tools.get_option(self.config, "showFrameStats", False) # Show frame statistics
        self._current_rig_date = None
        self._debug = Tools.get_option(self.config, "debug", False)

        # Set up the screen areas
        self._setup_ui()

        # Statistics instance (only used when switched on)
        if self._show_stats == True:
            self._stats = Statistics(Tools.get_option(self.config, "statsIntervalMillis", 2000), self.ui.area(DisplayAreas.STATISTICS))

        # Periodic update handler (the kemper is only asked when a certain time has passed)
        self._period = PeriodCounter(self.config["updateInterval"])

        # MIDI communication handler        
        self._midi = self._get_midi()

        # Kemper adapter to send and receive parameters
        self.kemper = Kemper(self._midi, self.config)

        # Set up switches
        self.switches = []
        self._init_switches()

    # Creates the display areas
    def _setup_ui(self):
        for area_def in DisplayAreaDefinitions:
            if area_def["id"] == DisplayAreas.STATISTICS and self._show_stats != True:
                continue
            self.ui.add_area_definition(area_def)

        self.ui.setup()

    # Initialize switches
    def _init_switches(self):
        if self._debug == True:
            Tools.print("-> Init switches")
                    
        for swDef in self.config["switches"]:
            self.switches.append(
                FootSwitch(
                    self, 
                    swDef
                )
            )

    # Start MIDI communication and return the handler
    def _get_midi(self):
        if self._debug == True:
            Tools.print("-> Init MIDI")

        return adafruit_midi.MIDI(
            midi_out    = usb_midi.ports[1],
            out_channel = self._midiChannel - 1,
            midi_in     = usb_midi.ports[0],
            in_buf_size = self._midi_buffer_size, 
            debug       = Tools.get_option(self.config, "debugMidi")
        )

    # Runs the processing loop (which never ends)
    def process(self):
        # Show user interface
        self.ui.show()

        if self._debug == True:
            Tools.print("-> Done initializing, starting processing loop")

        # Start processing loop
        while True:
            # If enabled, remember the tick starting time for statistics
            if self._show_stats == True:
                self._stats.start()

            # Receive MIDI messages
            midimsg = self._midi.receive()

            # Process the midi message
            self.kemper.receive(midimsg)

            # Process all switches 
            for switch in self.switches:
                switch.process(midimsg)
            
            # Update actions and rig info in a certain interval, less frequently then every tick
            if self._period.exceeded == True:
                self._update()

            # Output statistical info if enabled
            if self._show_stats == True:
                self._stats.finish()

    # Update (called on every periodic update interval)
    def _update(self):
        if self._debug == True:
            Tools.print(" -> Requesting rig date...")
        
        self.kemper.request(KemperMappings.MAPPING_RIG_DATE, self)

        # Update switch actions, so they can requests stuff themselves
        for switch in self.switches:
            switch.update()

    # Listen to Kemper value returns (rig name and date)
    def parameter_changed(self, mapping):
        # Rig name
        if mapping == KemperMappings.MAPPING_RIG_NAME:
            if self._debug == True:
                Tools.print(" -> Receiving rig name: " + mapping.value)

            self.ui.area(DisplayAreas.INFO).text = mapping.value

        # Rig date
        if mapping == KemperMappings.MAPPING_RIG_DATE:
            if self._debug == True:
                Tools.print(" -> Receiving rig date: " + mapping.value)

            if self._current_rig_date != mapping.value:
                if self._debug == True:
                    Tools.print("   -> Rig date was different from " + repr(self._current_rig_date) + ", requesting rig name, too...")                
                    Tools.print("     -> Requesting rig name...")
                
                self._current_rig_date = mapping.value
                self.kemper.request(KemperMappings.MAPPING_RIG_NAME, self)

    # Called when the Kemper is offline (requests took too long)
    def request_terminated(self, mapping):
        # Rig name
        if mapping == KemperMappings.MAPPING_RIG_NAME:
            if self._debug == True:
                Tools.print(" -> Request for rig name failed, is the device offline?")

            self.ui.area(DisplayAreas.INFO).text = KemperDefinitions.OFFLINE_RIG_NAME

        # Rig date
        if mapping == KemperMappings.MAPPING_RIG_DATE:
            if self._debug == True:
                Tools.print(" -> Request for rig date failed, is the device offline?")

            self._current_rig_date = None

    