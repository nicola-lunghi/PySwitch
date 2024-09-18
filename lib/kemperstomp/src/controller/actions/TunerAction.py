'''from .base.PushButtonAction import PushButtonAction
from ...model.Kemper import Kemper
from ...Tools import Tools
from ....config import Config
from ....definitions import KemperDefinitions, TunerActionModes


# Implements the effect enable/disable footswitch action
class TunerAction(PushButtonAction):
    
    def __init__(self, appl, switch, config):
        super().__init__(appl, switch, config)

        self._brightness_not_assigned = Config["ledBrightness"]["notAssigned"]
        self._brightness_on = Config["ledBrightness"]["on"]
        self._brightness_off = Config["ledBrightness"]["off"]

        self.label.text = KemperDefinitions.TUNER_MODE_NAME
        self.switch.color = Tools.dim_color(KemperDefinitions.TUNER_MODE_COLOR)
        self.switch.brightness = self._brightness_off

    def set(self, state):        
        self.appl.kemper.set_tuner_mode(state)
        self.update_displays()

    # Update display and switch
    def update_displays(self):
        if self.state == True:            
            self.switch.brightness = self._brightness_on
            
            if self.label != None:
                self.label.back_color = KemperDefinitions.TUNER_MODE_COLOR

        else:
            self.switch.brightness = self._brightness_off
            if self.label != None:
                self.label.back_color = Tools.dim_color(KemperDefinitions.TUNER_MODE_COLOR)
    

'''