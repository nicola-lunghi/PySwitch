from .DisplayLabel import DisplayLabel
from ..DisplayBounds import DisplayBounds
from ...core.controller.Updateable import Updateable
from ...core.misc.Tools import Tools
from ...core.client.ClientRequest import ClientRequestListener


# DisplayLabel which is connected to a client parameter
class ParameterDisplayLabel(DisplayLabel, Updateable, ClientRequestListener):
    
    # parameter: {
    #     "mapping":     A ClientParameterMapping instance whose values should be shown in the area
    #     "depends":     Optional. If a ClientParameterMapping instance is passed, the display is only updated
    #                    when this mapping's value has changed.
    #     "textOffline": Text to show initially and when the client is offline
    #     "textReset":   Text to show when a reset happened (on rig changes etc.)
    # }
    def __init__(self, parameter, bounds = DisplayBounds(), layout = {}, name = "", id = 0):
        super().__init__(bounds=bounds, layout=layout, name=name, id=id)

        self._mapping = parameter["mapping"]
        self._depends = Tools.get_option(parameter, "depends", None)

        self._last_value = None
        self._depends_last_value = None

        self._text_offline = Tools.get_option(parameter, "textOffline", "")
        self._text_reset = Tools.get_option(parameter, "textReset", "")        
    
    # We need access to the client, so we store appl here
    def init(self, ui, appl):
        super().init(ui, appl)

        self.text = self._text_offline
        
        self._appl = appl
        self._debug = Tools.get_option(appl.config, "debugParameters", False)

    # Called on every update tick
    def update(self):
        if not self._depends:
            self._appl.client.request(self._mapping, self)
        else:
            self._appl.client.request(self._depends, self)

    # Reset the parameter display
    def reset(self):
        self._last_value = None
        self._depends_last_value = None
        self.text = self._text_reset

        if self._debug:
            self._print(" -> Reset parameter " + self._mapping.name)

    # Listen to client value returns (rig name and date)
    def parameter_changed(self, mapping):
        if mapping == self._mapping and mapping.value != self._last_value:
            # Main mapping changed
            if self._debug:
                self._print(" -> " + mapping.name + " has changed: " + repr(mapping.value))

            self._last_value = mapping.value

            # Set value on display
            self.text = mapping.value

        if mapping == self._depends and mapping.value != self._depends_last_value:
            # Dependency has changed: Request update of main mapping
            if self._debug:
                self._print("   -> Dependency (" + mapping.name + ") has changed to " + repr(mapping.value) + ", requesting " + self._mapping.name + "...")

            self._depends_last_value = mapping.value        
            
            self._appl.client.request(self._mapping, self)

    # Called when the client is offline (requests took too long)
    def request_terminated(self, mapping):
        self.text = self._text_offline

        self._last_value = None
        self._depends_last_value = None

        if self._debug:
            self._print(" -> Request for " + mapping.name + " failed, is the device offline?")

    # Debug console output
    def _print(self, msg):
        Tools.print(self.__class__.__name__ + ": " + msg)
