from ...misc import Updateable

from adafruit_midi.system_exclusive import SystemExclusive

class EncoderAction(Updateable):

    # Use this action for all rotary encoders like wheels. The push-down switch of the encoder is 
    # not addressed here: This is represented as a separate switch, and can be linked to the same actions as a normal foot switch.
    def __init__(self, 
                 mapping,                           # Parameter mapping to be controlled
                 min_value = 0,                     # Minimum value of the mapping
                 max_value = None,                  # Maximum value of the mapping (set to None for auto-detect: 16383 for NRPN, 127 for CC)
                 step_width = None,                 # Increment/Decrement for one encoder step. Set to None for auto-detect (NRPN: 80, CC: 1)
                 enable_callback = None,            # Callback to set enabled state (optional). Must contain an enabled(action) function.
                 id = None,
                 accept_action = None,              # Action to acknowledge the entered value. If None, the encoder directly sets values as you turn it. 
                                                    # If you pass an Encoder Button action, the value will just be displayed and the MIDI command to set 
                                                    # it will be sent when the Button action is triggered.
                                                    # 
                                                    # If you use this, you will also need a preview display label (see below)
                 cancel_action = None,              # Action to cancel a preselection (only makes sense with accept_action set). Must also be of type Encoder Button.
                 preview_display = None,            # If assigned, the adjusted value will be displayed in the passed DisplayLabel when the encoder is adjusted. 
                                                    # This just makes sense in conjunction with an accept action (see above).
                 preview_timeout_millis = 1500,     # This is the amount of time (milliseconds) after which the preview display will return to its normal state.
                 preview_blink_period_millis = 400, # Blink period for preview (if an accept action is set)
                 preview_blink_color = (200, 200, 200), # Alternative color to be used when blinking.
                 preview_reset_mapping = None,      # A parameter mapping (optional) which will be tracked. If the value changes, the preselect mode will be reset.
                 convert_value = None               # Optional conversion routine for displaying values: (value) => string
        ):
        if isinstance(mapping.set, SystemExclusive):
            if max_value == None:
                max_value = 16383
            if step_width == None:
                step_width = 80
        else:
            if max_value == None:
                max_value = 127
            if step_width == None:
                step_width = 1

        self.id = id
        self._mapping = mapping
        self.__min_value = min_value
        self.__max_value = max_value
        self.__step_width = step_width

        self.__enable_callback = enable_callback
        if self.__enable_callback:
            self.__enable_callback.action = self

        self.__last_pos = -1
        self._last_value = -1
        self.__convert_value = convert_value

        if accept_action:
            accept_action.callback.register_encoder(self, False)

        if cancel_action:
            cancel_action.callback.register_encoder(self, True)
            
        self.__preselect = (accept_action != None)
        self.__preselect_active = False

        if preview_display:
            from ..preview import ValuePreview

            self.__preview = ValuePreview.get(preview_display)
            self.__preview_timeout_millis = preview_timeout_millis
            self.__blink_interval_millis = preview_blink_period_millis
            self.__blink_color = preview_blink_color
                
            if accept_action:
                self.__preview_reset_mapping = preview_reset_mapping
                self.__preview_reset_last_value = None
        else:
            self.__preview = None
                
    @property
    def enabled(self):
        return self.__enable_callback.enabled(self) if self.__enable_callback else True

    def init(self, appl):
        self._appl = appl

        appl.client.register(self._mapping)

        if self.__preview and self.__preselect and self.__preview_reset_mapping:
            appl.client.register(self.__preview_reset_mapping)

    def update(self):
        self._appl.client.request(self._mapping)

        if self.__preview:
            self.__preview.update()

    def _get_value(self):
        return self._mapping.value

    def _set_value(self, value):
        self._mapping.value = value

    # Process the current encoder position
    def process(self, position):
        if self.__last_pos == -1:
            self.__last_pos = position

        if self.__preview and self.__preselect and self.__preview_reset_mapping:
            if self.__preview_reset_mapping.value != self.__preview_reset_last_value:
                if self.__preview_reset_mapping.value != None and self.__preview_reset_last_value != None:
                    self.cancel()

                self.__preview_reset_last_value = self.__preview_reset_mapping.value

        if self.__last_pos == position:
            return
                        
        if self._get_value() == None:
            self._set_value(0)
            
        add_value = (position - self.__last_pos) * self.__step_width        
        self.__last_pos = position

        if not self.__preselect:
            v = self._get_value() + add_value #  sdcsdvsdv
        else:
            v = self._last_value + add_value

        if v < self.__min_value:
            v = self.__min_value
        if v > self.__max_value:
            v = self.__max_value

        if self._last_value != v:
            self._last_value = v
            
            if not self.__preselect:
                self.accept()
            else:
                self.__preselect_active = True

            if self.__preview:
                if not self.__convert_value:
                    self.__preview.preview_mapping(
                        mapping = self._mapping,
                        value = v,
                        max_value = self.__max_value,
                        client = self,
                        stay = self.__preselect,
                        timeout_millis = self.__preview_timeout_millis,
                        blink_interval_millis = self.__blink_interval_millis if self.__preselect else None,
                        blink_color = self.__blink_color
                    )
                else:
                    self.__preview.preview(
                        text = self.__convert_value(v),
                        client = self,
                        stay = self.__preselect,
                        timeout_millis = self.__preview_timeout_millis,
                        blink_interval_millis = self.__blink_interval_millis if self.__preselect else None,
                        blink_color = self.__blink_color
                    )

    # Send the last value and reset preview display
    def accept(self):
        if self._last_value == -1:
            return
        
        if self.__preselect and not self.__preselect_active:
            return
        
        # Send message
        self._appl.client.set(self._mapping, self._last_value)
        self._set_value(self._last_value)

        self.cancel(immediately = False)

    # Cancel preselection
    def cancel(self, immediately = True):
        self.__preselect_active = False

        self._last_value = self._get_value()

        if self.__preview:
            self.__preview.reset(immediately = immediately)
