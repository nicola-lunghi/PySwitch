##############################################################################################################################################
# 
# Definition of communication wrappers. This is where the client specific (i.e. Kemper) implementations are linked to the framework.
#
##############################################################################################################################################

from kemper import KemperMidiValueProvider, KemperBidirectionalProtocol


Communication = {

    # Value provider which is responsible for setting values on MIDI messages for value changes, and parse MIDI messages
    # when an answer to a value request is received.
    "valueProvider": KemperMidiValueProvider(),

    # Optional: Protocol to use. If not specified, the standard Client protocol is used which requests all
    # parameters in each update cycle. Use this to implement bidirectional communication.
    "protocol": KemperBidirectionalProtocol(
        time_lease_seconds = 10               # When the controller is removed, the Profiler will stay in bidirectional
                                              # mode for this amount of seconds. The communication is re-initiated every 80% 
                                              # of this value. 
    )
}
