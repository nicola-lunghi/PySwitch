import time
import usb_midi
import adafruit_midi 

from ..hardware.LedDriver import LedDriver
from ..model.FootSwitch import FootSwitch
from ..model.KemperProfilerPlayer import KemperProfilerPlayer


# Main application class (controls the processing)    
class KemperStompController:
    def __init__(self, ui, config):
        self.ui = ui
        self.config = config
                    
        self.led_driver = LedDriver(self.config["neoPixelPort"], len(self.config["switches"]) * FootSwitch.NUM_PIXELS)    # NeoPixel driver 
        self.switches = []                                        # Array of registered switches
        
        self._last_update = 0                                     # Used to store the last update timestamp
        self._update_interval = self.config["updateInterval"]     # Update interval (seconds)
        self._midiChannel = self.config["midiChannel"]            # MIDI channel to use
        self._midi_buffer_size = self.config["midiBufferSize"]    # MIDI buffer size (default: 60)
        self._midi_usb = self._get_midi()                         # MIDI communication handler
        
        self.kemper = KemperProfilerPlayer(self._midi_usb)        # Kemper adapter instance (implements communication with the Profiler)

        # Set up switches
        self._init_switches()

    # Initialize switches
    def _init_switches(self):
        for swDef in self.config["switches"]:
            self.switches.append(
                FootSwitch(
                    self, 
                    swDef
                )
            )

    # Start MIDI communication and return the handler
    def _get_midi(self):
        return adafruit_midi.MIDI(
            midi_out    = usb_midi.ports[1],
            out_channel = self._midiChannel - 1,
            midi_in     = usb_midi.ports[0],
            in_buf_size = self._midi_buffer_size, 
            debug       = False
        )

    # Runs the processing loop (which never ends)
    def process(self):
        # Show user interface
        self.ui.show()

        # Start processing loop
        while True:            
            self._tick()

    # Processing loop implementation
    def _tick(self):
        start_time = self._get_current_millis()

        # Receive MIDI messages
        midimsg = self._midi_usb.receive()

        # Receive rig name / date
        self._parse_rig_info(midimsg)

        # Process all switches
        for switch in self.switches:
            switch.process(midimsg)
        
        # Update rig info in a certain interval
        if self._last_update + self._update_interval < start_time:
            self._last_update = start_time
            self.kemper.request_rig_date()

        # Output debug info
        self.ui.debug(str(int((self._get_current_millis() - start_time) * 1000)) + "ms")

    # Parse rig info messages
    def _parse_rig_info(self, midi_message):
        if midi_message == None:
            return
        
        rig_name = self.kemper.parse_rig_name(midi_message)
        if rig_name != None:
            self.ui.rig_name = rig_name.value

        rig_date = self.kemper.parse_rig_date(midi_message)
        if rig_date != None:
            if self.ui.rig_date != rig_date.value:
                self.ui.rig_date = rig_date.value
                self.kemper.request_rig_info()

    # Returns a current timestmap in milliseconds
    def _get_current_millis(self):
        return time.monotonic()
    