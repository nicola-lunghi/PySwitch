#################################################################################################################################
# 
# Global kemper configuration for the KemperStomp script: definitions of kemper MIDI addresses, effect categories and a defaulted
# SysEx message class to be used in mappings for convenience. The MIDI message composition/parsing is also implemented here.
#
#################################################################################################################################

from adafruit_midi.system_exclusive import SystemExclusive
from .Kemper import Kemper

#################################################################################################################################

# Kemper specific SysEx message with defaults which are valid most of the time
class KemperNRPNMessage(SystemExclusive):
    # Takes MIDI messages as argument (CC or SysEx)
    def __init__(
            self, 
            function_code,
            address_page,
            address_number,
            manufacturer_id = Kemper.NRPN_MANUFACTURER_ID, 
            product_type = Kemper.NRPN_PRODUCT_TYPE_PROFILER_PLAYER,
            device_id = Kemper.NRPN_DEVICE_ID_OMNI
        ):

        # Adafruit SystemExclusive
        super().__init__(
            manufacturer_id,                 # [0x00, 0x20, 0x33]
            [
                product_type,                # 0x02 (Player), 0x00 (Profiler)
                device_id,                   # 0x7f (omni) or manually set via parameter
                function_code,               # Selects the function, for example 0x41 for requesting a single parameter
                Kemper.NRPN_INSTANCE,   # 0x00
                address_page,                # Controller MSB (address page)
                address_number               # Controller LSB (address number of parameter)
            ]
        )
        
