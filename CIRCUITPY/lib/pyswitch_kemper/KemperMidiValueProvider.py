#################################################################################################################################
# 
# Global kemper configuration for the KemperStomp script: definitions of kemper MIDI addresses, effect categories and a defaulted
# SysEx message class to be used in mappings for convenience. The MIDI message composition/parsing is also implemented here.
#
#################################################################################################################################

import math

from adafruit_midi.control_change import ControlChange
from adafruit_midi.system_exclusive import SystemExclusive

from .Kemper import Kemper
from pyswitch.core.client.Client import ClientValueProvider

#################################################################################################################################


# Implements setting values and parsing request responses
class KemperMidiValueProvider(ClientValueProvider):

    # Must parse the incoming MIDI message and return the value contained.
    # If the response template does not match, must return None.
    # Must return True to notify the listeners of a value change.
    def parse(self, mapping, midi_message):
        # Compare manufacturer IDs
        if midi_message.manufacturer_id != mapping.response.manufacturer_id:
            return False
        
        # Get data as integer list from both the incoming message and the response
        # template in the mapping (both messages are SysEx anytime)
        response = list(midi_message.data)                        
        template = list(mapping.response.data)        

        # The first two values are ignored (the Kemper MIDI specification implies this would contain the product type
        # and device ID as for the request, however the device just sends two zeroes)

        # Check if the message belongs to the mapping. The following have to match:
        #   2: function code, 
        #   3: instance ID, 
        #   4: address page, 
        #   5: address nunber
        if response[2:6] != template[2:6]:
            return False
        
        # The values starting from index 6 are the value of the response.
        if mapping.type == Kemper.NRPN_PARAMETER_TYPE_STRING:
            # Take as string
            mapping.value = ''.join(chr(int(c)) for c in response[6:-1])
        else:
            # Decode 14-bit value to int
            mapping.value = response[-2] * 128 + response[-1]

        return True
    
    # Must set the passed value on the SET message of the mapping.
    def set_value(self, mapping, value):
        if isinstance(mapping.set, ControlChange):
            # Set value directly (CC takes int values)
            mapping.set.value = value

        elif isinstance(mapping.set, SystemExclusive):            
            # Fill up message to appropriate length for the specification
            data = list(mapping.set.data)
            while len(data) < 8:
                data.append(0)
            
            # Set value as 14 bit
            data[6] = int(math.floor(value / 128))
            data[7] = int(value % 128)

            mapping.set.data = bytes(data)
        
