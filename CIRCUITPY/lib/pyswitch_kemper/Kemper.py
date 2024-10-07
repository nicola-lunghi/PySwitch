
# Some basic Kemper MIDI addresses and values
class Kemper:
    NRPN_PRODUCT_TYPE_PROFILER = 0x00         # Kemper Profiler
    NRPN_PRODUCT_TYPE_PROFILER_PLAYER = 0x02  # Kemper Profiler Player
    NRPN_DEVICE_ID_OMNI = 0x7f                # Omni (all devices, only supported mode)
    NRPN_INSTANCE = 0x00                      # Instance ID for NRPN. The profiler only supports instance 0.
    NRPN_MANUFACTURER_ID = [0x00, 0x20, 0x33]             # Kemper manufacturer ID

    # Parameter types
    NRPN_PARAMETER_TYPE_NUMERIC = 0   # Default, also used for on/off
    NRPN_PARAMETER_TYPE_STRING = 1

    # Generally used NRPN values
    NRPN_PARAMETER_OFF = 0
    NRPN_PARAMETER_ON = 1

    # Helper to convert values in range [0..1] to the NRPN value range of [0..16383]
    def NRPN_VALUE(value):
        return int(16383 * value)
