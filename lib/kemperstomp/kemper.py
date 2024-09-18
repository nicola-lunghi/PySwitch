#################################################################################################################################
# 
# Global kemper configuration for the KemperStomp script.
#
#################################################################################################################################

from .definitions import KemperMidi

KemperConfig = {

    # Specifies the Kemper product to control
    "kemperProductType": KemperMidi.NRPN_PRODUCT_TYPE_PROFILER_PLAYER,

    # Kemper device ID (see system page of the profiler). DEVICE_ID_OMNI addresses all devices.
    "kemperDeviceId": KemperMidi.NRPN_DEVICE_ID_OMNI,

}
