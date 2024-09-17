from ..config import Config

# Generic tools
class Tools:
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
