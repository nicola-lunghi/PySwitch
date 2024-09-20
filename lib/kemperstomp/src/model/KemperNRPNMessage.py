from adafruit_midi.system_exclusive import SystemExclusive

from ...definitions import KemperMidi
from ...kemper import KemperConfig

# Kemper specific SysEx message
class KemperNRPNMessage(SystemExclusive):
    # Takes MIDI messages as argument (CC or SysEx)
    def __init__(
            self, 
            function_code,
            address_page,
            address_number,
            manufacturer_id = KemperMidi.NRPN_MANUFACTURER_ID, 
            product_type = KemperConfig["kemperProductType"],
            device_id = KemperConfig["kemperDeviceId"],
        ):

        # Adafruit SystemExclusive
        super().__init__(
            manufacturer_id,                 # [0x00, 0x20, 0x33]
            [
                product_type,                # 0x02 (Player), 0x00 (Profiler)
                device_id,                   # 0x7f (omni) or manually set via parameter
                function_code,               # Selects the function, for example 0x41 for requesting a single parameter
                KemperMidi.NRPN_INSTANCE,    # 0x00
                address_page,                # Controller MSB (address page)
                address_number               # Controller LSB (address number of parameter)
            ]
        )
        