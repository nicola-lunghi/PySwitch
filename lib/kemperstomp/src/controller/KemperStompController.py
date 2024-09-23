import usb_midi
import adafruit_midi 

from .FootSwitch import FootSwitch
from .Statistics import Statistics
from .PeriodCounter import PeriodCounter
from .InfoParameterController import InfoParameterController
from ..hardware.LedDriver import LedDriver
from ..model.Kemper import Kemper
from ..model.KemperRequest import KemperRequestListener
from ..Tools import Tools
from ...definitions import KemperDefinitions, FootSwitchDefaults
from ...display import DisplayAreas, DisplayAreaDefinitions


# Main application class (controls the processing)    
class KemperStompController(KemperRequestListener):
    def __init__(self, ui, config):
        self.ui = ui
        self.config = config

        # NeoPixel driver 
        self.led_driver = LedDriver(self.config["neoPixelPort"], len(self.config["switches"]) * FootSwitchDefaults.NUM_PIXELS)    
        
        self._midiChannel = self.config["midiChannel"]                            # MIDI channel to use
        self._midi_buffer_size = self.config["midiBufferSize"]                    # MIDI buffer size (default: 60)
        self._show_stats = Tools.get_option(self.config, "showFrameStats", False) # Show frame statistics
        self._debug = Tools.get_option(self.config, "debug", False)

        # Periodic update handler (the kemper is only asked when a certain time has passed)
        self._period = PeriodCounter(self.config["updateInterval"])

        # MIDI communication
        self._init_midi()

        # Kemper adapter to send and receive parameters
        self.kemper = Kemper(self._midi, self.config)

        # Set up the screen areas
        self._prepare_ui()

        # Statistics instance (only used when switched on)
        if self._show_stats == True:
            self._stats = Statistics(Tools.get_option(self.config, "statsIntervalMillis", 2000), self.ui.area(DisplayAreas.STATISTICS))

        # Controller for the display areas
        self._info_parameters = InfoParameterController(
            self,
            Tools.get_option(self.config, "displays", []),
            Tools.get_option(self.config, "debugParameters", False)
        )

        # Set up switches
        self.switches = []
        self._init_switches()

    # Creates the display areas
    def _prepare_ui(self):
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
            Tools.print("-> Init UI")

        # Show user interface
        self.ui.show()

        if self._debug == True:
            Tools.print("-> Done initializing, starting processing loop")

        # Start processing loop
        while True:
            # If enabled, remember the tick starting time for statistics
            if self._show_stats == True:
                self._stats.start()

            # Receive all available MIDI messages            
            cnt = 0
            while True:
                midimsg = self._midi.receive()

                # Process the midi message
                self.kemper.receive(midimsg)

                cnt = cnt + 1
                if midimsg == None or cnt > KemperDefinitions.MAX_NUM_CONSECUTIVE_MIDI_MESSAGES:
                    break            
        
            # Process all switches 
            for switch in self.switches:
                switch.process()
            
            # Update kemper parameters in periodic intervals, less frequently then every tick
            if self._period.exceeded == True:
                self._update()

            # Output statistical info if enabled
            if self._show_stats == True:
                self._stats.finish()


    # Update (called on every periodic update interval)
    def _update(self):
        if self._debug == True:
            Tools.print(" -> Requesting rig date...")
        
        # Update displayed parameters
        self._info_parameters.update()

        # Update switch actions
        for switch in self.switches:
            switch.update()
