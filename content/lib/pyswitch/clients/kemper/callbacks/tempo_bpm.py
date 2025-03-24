from ....controller.callbacks.parameter_display import ParameterDisplayCallback

from ..mappings.tempo_bpm import MAPPING_TEMPO_BPM

class KemperTempoDisplayCallback(ParameterDisplayCallback):
    def __init__(self):
        def convert_value(value):
            return f"{ str(value) } bpm"
        
        super().__init__(
            mapping = MAPPING_TEMPO_BPM(), 
            convert_value = convert_value
        )
