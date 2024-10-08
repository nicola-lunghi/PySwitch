from .DisplayLabel import DisplayLabel
from ..DisplayBounds import DisplayBounds
from ...core.controller.measurements import RuntimeMeasurementListener, RuntimeMeasurement
from ...core.controller.Updateable import Updateable


# DisplayLabel which is connected to a client parameter
class StatisticsDisplayLabel(DisplayLabel, RuntimeMeasurementListener, Updateable):
    
    def __init__(self, measurements, bounds = DisplayBounds(), layout = {}, id = 0):
        super().__init__(bounds=bounds, layout=layout, name="Statistics", id=id)        
    
        for m in measurements:
            if not isinstance(m, RuntimeMeasurement):
                continue
            
            m.add_listener(self)

        self._measurements = measurements

        self._texts = ["" for m in measurements]
        self._current_texts = ["" for m in measurements]

    # Add measurements to controller
    def init(self, ui, appl):
        super().init(ui, appl)

        for m in self._measurements:
            appl.add_runtime_measurement(m)

    def update(self):
        for i in range(len(self._texts)):
            if self._current_texts[i] != self._texts[i]:
                self._update_text()
                return

    def _update_text(self):
        lines = []
        for i in range(len(self._measurements)):
            self._current_texts[i] = self._texts[i]
            
            lines.append(self._texts[i])

        self.text = "\n".join(lines)    

    def measurement_updated(self, measurement):
        for i in range(len(self._measurements)):
            m = self._measurements[i]

            if not isinstance(m, RuntimeMeasurement):
                self._texts[i] = m.get_message()
            else:    
                if m != measurement:
                    continue
                
                self._texts[i] = m.get_message()
        


