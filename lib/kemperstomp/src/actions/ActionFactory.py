
from ...kemperstomp_def import Actions

# Factory for Action Implementations
class ActionFactory:

    # Returns an action instance (featuring a process(midi_message) method), according to the passed action configuration.
    def get(self, appl, switch, config):
        type = config["type"]

        if type == Actions.EFFECT_ON_OFF:
            # Enable/disable an effect slot
            from .EffectEnableAction import EffectEnableAction
            return EffectEnableAction(appl, switch, config)
        
        elif type == Actions.REBOOT:
            # Reboot the device
            from .RebootAction import RebootAction
            return RebootAction(appl, switch, config)
        
        elif type == Actions.EXPLORE_IO:
            # Print port name to console
            from .ExploreIoAction import ExploreIoAction
            return ExploreIoAction(appl, switch, config)
        
        elif type == Actions.EXPLORE_PIXELS:
            # Scan pixels and print currently shown one to the console
            from .ExplorePixelAction import ExplorePixelAction
            return ExplorePixelAction(appl, switch, config)
        
        elif type == Actions.PRINT:
            # Print a simple string to the console
            from .PrintAction import PrintAction
            return PrintAction(appl, switch, config)
        
        else:
            raise Exception("Invalid action type: " + type + ", is this defined in kemperstomp_def.py?")