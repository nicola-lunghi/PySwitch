from ....controller.actions.EncoderAction import EncoderAction
from ..mappings.select import MAPPING_BANK_SELECT
from .. import NUM_BANKS, NUM_RIGS_PER_BANK

# Preselects the bank with a rotary encoder. 
# 
# After this, the bank change will be done after a rig has been selected.
def ENCODER_BANK_SELECT(
    enable_callback = None,
    id = None
):
    return _BankSelectEncoderAction(
        enable_callback = enable_callback,
        id = id
    )


class _BankSelectEncoderAction(EncoderAction):

    def __init__(self,
                 enable_callback = None,
                 id = None
    ):
        super().__init__(
            mapping = MAPPING_BANK_SELECT(),
            step_width = 1,
            max_value = NUM_BANKS - 1,
            enable_callback = enable_callback,
            id = id
        )
        
    def accept(self):
        super().accept()

        if self._last_value == -1:
            return

        self._appl.shared["preselectCallback"] = self        
        self._appl.shared["preselectedBank"] = self._last_value

    def _get_value(self):
        return int(self._mapping.value / NUM_RIGS_PER_BANK)

    def _set_value(self, value):
        self._mapping.value = value * NUM_RIGS_PER_BANK


