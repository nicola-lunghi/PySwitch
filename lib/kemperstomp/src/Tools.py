import time
from ..config import Config

# Generic tools
class Tools:

    DIM_FACTOR = -1

    # Read a value from an option dictionary with an optional default value
    @staticmethod
    def get_option(config, name, default = False):
        if name not in config:
            return default        
        return config[name]

    # Print if we are in console mode    
    @staticmethod
    def print(msg):
        if Tools.get_option(Config, "debug") != True:
            return
        print(msg)

    # Returns a current timestmap in integer milliseconds
    @staticmethod
    def get_current_millis():
        return int(time.monotonic() * 1000)
    
    # Dims a passed color for display of disabled state
    @staticmethod
    def dim_color(color):
        if Tools.DIM_FACTOR == -1:
            Tools.DIM_FACTOR = Config["displayDimFactor"]

        return (
            int(color[0] * Tools.DIM_FACTOR),
            int(color[1] * Tools.DIM_FACTOR),
            int(color[2] * Tools.DIM_FACTOR)
        )
