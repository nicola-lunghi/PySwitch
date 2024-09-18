import usb_midi
import adafruit_midi 

from .FootSwitch import FootSwitch
from ..hardware.LedDriver import LedDriver
from ..model.Kemper import Kemper
from ..Tools import Tools
from ...config import Config
from ...mappings import KemperMappings

# Main application class (controls the processing)    
class KemperStompController:
    def __init__(self, ui, config):
        self.ui = ui
        self.config = config

        # NeoPixel driver 
        self.led_driver = LedDriver(self.config["neoPixelPort"], len(self.config["switches"]) * FootSwitch.NUM_PIXELS)    
        
        self._last_update = 0                                     # Used to store the last update timestamp
        self._update_interval_millis = self.config["updateInterval"]     # Update interval (milliseconds)
        self._midiChannel = self.config["midiChannel"]            # MIDI channel to use
        self._midi_buffer_size = self.config["midiBufferSize"]    # MIDI buffer size (default: 60)
        self._current_rig_date = None

        # MIDI communication handler        
        self._midi = self._get_midi()

        # Kemper interface
        self.kemper = Kemper(self._midi)

        # Set up switches
        self.switches = []                                        # Array of registered switches        
        self._init_switches()

    # Initialize switches
    def _init_switches(self):
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
        Tools.print("-> Init MIDI")

        return adafruit_midi.MIDI(
            midi_out    = usb_midi.ports[1],
            out_channel = self._midiChannel - 1,
            midi_in     = usb_midi.ports[0],
            in_buf_size = self._midi_buffer_size, 
            debug       = Tools.get_option(Config, "debugMidi")
        )

    # Runs the processing loop (which never ends)
    def process(self):
        # Show user interface
        self.ui.show()

        Tools.print("-> Done initializing, starting processing loop")

        # Start processing loop
        while True:            
            self._tick()

    # Processing loop implementation
    def _tick(self):
        start_time = Tools.get_current_millis()

        # Receive MIDI messages
        midimsg = self._midi.receive()

        # Receive rig name / date
        self._parse_rig_info(midimsg)

        # Process all switches
        for switch in self.switches:
            switch.process(midimsg)
        
        # Update rig info in a certain interval
        if self._last_update + self._update_interval_millis < start_time:
            self._last_update = start_time
            self.kemper.request(KemperMappings.MAPPING_RIG_DATE)

            # Update switch actions
            for switch in self.switches:
                switch.update()

        # Output statistical info
        self.ui.set_stats(Tools.get_current_millis() - start_time)

    # Parse rig info messages
    def _parse_rig_info(self, midi_message):
        if midi_message == None:
            return
                
        rig_name = self.kemper.parse(KemperMappings.MAPPING_RIG_NAME, midi_message)
        if rig_name != None:
            Tools.print(" -> Receiving rig name: " + rig_name)
            self.ui.info_text = rig_name

        rig_date = self.kemper.parse(KemperMappings.MAPPING_RIG_DATE, midi_message)
        if rig_date != None:
            Tools.print(" -> Receiving rig date: " + rig_date)
            if self._current_rig_date != rig_date:
                Tools.print("   -> Rig date was different from " + repr(self._current_rig_date) + ", requesting rig name, too...")
                self._current_rig_date = rig_date
                
                self.kemper.request(KemperMappings.MAPPING_RIG_NAME)


    