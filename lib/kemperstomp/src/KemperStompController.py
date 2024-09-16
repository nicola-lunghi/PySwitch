import time

import usb_midi
import adafruit_midi 

from .hardware.LedDriver import LedDriver
from .model.FootSwitch import FootSwitch
from .model.KemperProfilerPlayer import KemperProfilerPlayer

from ..kemperstomp_config import Config


# Main application class (controls the processing)    
class KemperStompController:
    def __init__(self, ui):
        self.ui = ui
            
        # NeoPixel driver 
        self.led_driver = LedDriver(Config["neoPixelPort"], len(Config["switches"]) * FootSwitch.NUM_PIXELS)

        # Initialize MIDI
        self._init_midi()

        # Kemper adapter instance
        self.kemper = KemperProfilerPlayer(self.midi_usb)

        # Set up switches
        self._init_switches()

        # Reset timer for rig info sensing (seconds)
        self.last_update = 0
        self.update_interval = Config["updateInterval"]

    # Initialize switches
    def _init_switches(self):
        self.switches = []

        for swDef in Config["switches"]:
            self.switches.append(
                FootSwitch(
                    self, 
                    swDef
                )
            )

    # Start MIDI communication
    def _init_midi(self):
        self.midiChannel = Config["midiChannel"]
        
        self.midi_usb = adafruit_midi.MIDI(
            midi_out    = usb_midi.ports[1],
            out_channel = self.midiChannel - 1,
            midi_in     = usb_midi.ports[0],
            in_buf_size = Config["midiBufferSize"], 
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
        midimsg = self.midi_usb.receive()

        # Receive rig name / date
        self._parse_rig_info(midimsg)

        # Process all switches
        for switch in self.switches:
            switch.process(midimsg)
        
        # Update rig info in a certain interval
        if self.last_update + self.update_interval < start_time:
            self.last_update = start_time
            self.kemper.request_rig_date()

        # Output debug info
        self.ui.debug(str(int((self._get_current_millis() - start_time) * 1000)) + "ms")

    # Parse rig info messages
    def _parse_rig_info(self, midi_message):
        if midi_message == None:
            return
        
        rig_name = self.kemper.parse_rig_name(midi_message)
        if rig_name != None:
            self.ui.set_rig_name(rig_name.value)

        rig_date = self.kemper.parse_rig_date(midi_message)
        if rig_date != None:
            if self.ui.set_rig_date(rig_date.value) == True:
                self.kemper.request_rig_info()

    # Returns a current timestmap in milliseconds
    def _get_current_millis(self):
        return time.monotonic()
    