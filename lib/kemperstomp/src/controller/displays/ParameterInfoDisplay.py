from ...misc.Tools import Tools
from ...client.ClientRequest import ClientRequestListener
from .base.InfoDisplay import InfoDisplay


# Manages the display areas of the program, updating their values.
class ParameterInfoDisplay(ClientRequestListener, InfoDisplay):

    # config: {
    #     "mapping": A ClientParameterMapping instance whose values should be shown in the area
    #     "depends": Optional. If a ClientParameterMapping instance is passed, the display is only updated
    #                when this mapping's value has changed.
    #     "display": Display area addressing (see UserInterface.setup_label())
    #                {
    #                      "area": ...
    #                      "index": ...
    #                }
    #     "textOffline": Text to show initially and when the client is offline
    #     "textReset": Text to show when a reset happened (on rig changes etc.)
    # }
    def __init__(self, appl, config, debug):
        self._appl = appl
        self._config = config
        self._debug = debug
        
        self._mapping = self._config["mapping"]
        self._depends = Tools.get_option(self._config, "depends", None)

        self._last_value = None
        self._depends_last_value = None

        self._text_offline = Tools.get_option(self._config, "textOffline", "")
        self._text_reset = Tools.get_option(self._config, "textReset", "")

        self._label = self._appl.ui.root.search(self._config["display"])
        self._label.text = self._text_offline

    # Called on every update period
    def update(self):
        if self._depends == None:
            self._appl.client.request(self._mapping, self)
        else:
            self._appl.client.request(self._depends, self)

    # Reset the parameter display
    def reset(self):
        self._last_value = None
        self._depends_last_value = None
        self._label.text = self._text_reset

        if self._debug == True:
            self._print(" -> Reset parameter " + self._mapping.name)

    # Listen to client value returns (rig name and date)
    def parameter_changed(self, mapping):
        if mapping == self._mapping and mapping.value != self._last_value:
            # Main mapping changed
            if self._debug == True:
                self._print(" -> " + mapping.name + " has changed: " + repr(mapping.value))

            self._last_value = mapping.value

            # Set value on display
            self._label.text = mapping.value

        if mapping == self._depends and mapping.value != self._depends_last_value:
            # Dependency has changed: Request update of main mapping
            if self._debug == True:
                self._print("   -> Dependency (" + mapping.name + ") has changed to " + repr(mapping.value) + ", requesting " + self._mapping.name + "...")

            self._depends_last_value = mapping.value        
            
            self._appl.client.request(self._mapping, self)

    # Called when the client is offline (requests took too long)
    def request_terminated(self, mapping):
        self._label.text = self._text_offline

        self._last_value = None
        self._depends_last_value = None

        if self._debug == True:
            self._print(" -> Request for " + mapping.name + " failed, is the device offline?")

    # Debug console output
    def _print(self, msg):
        Tools.print("InfoParameter: " + msg)
