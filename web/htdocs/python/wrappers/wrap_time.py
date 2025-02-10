from time import localtime, monotonic
from js import externalRefs

class WrapTime:
    def monotonic(self):
        if externalRefs.hasOwnProperty("overrideMonotonic"):
            return externalRefs.overrideMonotonic()
        
        return monotonic()
    
    def localtime(self, seconds):
        return localtime(seconds)