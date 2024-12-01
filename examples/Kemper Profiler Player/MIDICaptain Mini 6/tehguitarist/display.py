##############################################################################################################################################
# 
# Definition of display elememts.
#
##############################################################################################################################################

from micropython import const
from pyswitch.misc import DEFAULT_LABEL_COLOR #, Colors

from pyswitch.ui.elements import DisplaySplitContainer, DisplayBounds
from pyswitch.ui.elements import DisplayLabel, BIDIRECTIONAL_PROTOCOL_STATE_DOT, PERFORMANCE_DOT
from pyswitch.ui.ui import HierarchicalDisplayElement
from pyswitch.controller.callbacks import Callback
from pyswitch.clients.kemper import KemperRigNameCallback, TunerDisplayCallback, KemperMappings

#############################################################################################################################################

# Layout used for the action labels (only used here locally)
_ACTION_LABEL_LAYOUT = {
    "font": "/fonts/H20.pcf",
    "backColor": DEFAULT_LABEL_COLOR,
    "stroke": 1
}

DISPLAY_HEADER_1 = DisplayLabel(layout = _ACTION_LABEL_LAYOUT)
DISPLAY_HEADER_2 = DisplayLabel(layout = _ACTION_LABEL_LAYOUT)
DISPLAY_HEADER_3 = DisplayLabel(layout = _ACTION_LABEL_LAYOUT)
DISPLAY_FOOTER_1 = DisplayLabel(layout = _ACTION_LABEL_LAYOUT)
DISPLAY_FOOTER_2 = DisplayLabel(layout = _ACTION_LABEL_LAYOUT)
DISPLAY_FOOTER_3 = DisplayLabel(layout = _ACTION_LABEL_LAYOUT)

#############################################################################################################################################

# Some only locally used constants
_DISPLAY_WIDTH = const(240)
_DISPLAY_HEIGHT = const(240)
_SLOT_HEIGHT = const(40)                 # Slot height on the display

class _BankNameCallback(Callback):
    def __init__(self):
        Callback.__init__(self)
       
        # This defines that the following mappings have to be listened to.
        # In your case you need to listen to two mappings as you also need the amp name.        
        self._mapping_bank = KemperMappings.NEXT_BANK()
        self._mapping_amp_name = KemperMappings.AMP_NAME()

        self.register_mapping(self._mapping_bank)
        self.register_mapping(self._mapping_amp_name)

    # This will be called for updating the label whenever the mappings defined above
    # have changed.    
    def update_label(self, label):
        # This now also has to encounter the possibility that the bank mapping value is still None
        # (in case the amp name mapping gets a value first)
        current_bank = int(self._mapping_bank.value / 5) if self._mapping_bank.value != None else None
        amp_name = self._mapping_amp_name.value

        # Removed the if statement because get_custom_text always returns a value. Also
        # pass the amp name here (update_label gets called whenever one of the registered mappings has changed).
        # Beware that both values can be None now!
        label.text = self._get_custom_text(current_bank, amp_name)

    # Your bank name function. Both bank and amp_name can be None.
    def _get_custom_text(self, bank, amp_name):
        if bank == 0:
            return repr(bank + 1) + " - PAF"
        elif bank == 1:
            return repr(bank + 1) + " - P90"
        elif bank == 2:
            return repr(bank + 1) + " - EMG"
        elif bank == 3:
            return repr(bank + 1) + " - Wide-Range"
        elif bank == 4:
            return repr(bank + 1) + " - Bass"
        elif bank == 5:
            return repr(bank + 1) + " - Acoustic"
        else:
            # Standard behaviour for all other banks 
            # Here you now have also to check None state for both values or you config will crash:
            bank_display = repr(bank + 1) if bank else ""
            amp_name_display = repr(amp_name) if amp_name else ""
            
            return "Bank " + bank_display + " - " + amp_name_display
   

############################################################################################################################################
# The DisplayBounds class is used to easily layout the default display in a subtractive way. Initialize it with all available space:
_display_bounds = DisplayBounds(0, 0, _DISPLAY_WIDTH, _DISPLAY_HEIGHT)

_bounds = _display_bounds.clone()

Splashes = TunerDisplayCallback(
    splash_default = HierarchicalDisplayElement(
        bounds = _display_bounds,
        children = [
            # Header area (referenced by ID in the action configurations)
            DisplaySplitContainer(
                bounds = _bounds.remove_from_top(_SLOT_HEIGHT),
                children = [
                    DISPLAY_HEADER_1,
                    DISPLAY_HEADER_2,
                    DISPLAY_HEADER_3
                ]
            ),

            # Footer area (referenced by ID in the action configurations)
            DisplaySplitContainer(
                bounds = _bounds.remove_from_bottom(_SLOT_HEIGHT),
                children = [
                    DISPLAY_FOOTER_1,
                    DISPLAY_FOOTER_2,
                    DISPLAY_FOOTER_3
                ]
            ),

            # Bank/Amp name
            DisplayLabel(
                bounds = _bounds.remove_from_bottom(50),
                layout = {
                    "font": "/fonts/H20.pcf",
                    "maxTextWidth": 230, 
                },
                callback = _BankNameCallback()
            ),

            # Rig name
            DisplayLabel(
                bounds = _bounds,
                layout = {
                    "font": "/fonts/PTSans-NarrowBold-40.pcf",
                    "lineSpacing": 0.8,
                    "maxTextWidth": 230,
                    "text": KemperRigNameCallback.DEFAULT_TEXT,
                },
                callback = KemperRigNameCallback()
            ),


            # Bidirectional protocol state indicator (dot)
            BIDIRECTIONAL_PROTOCOL_STATE_DOT(_bounds.translated(0, -130)),

            # Performance indicator (dot)
            PERFORMANCE_DOT(_bounds.translated(0, -123)),
        ]
    )
)