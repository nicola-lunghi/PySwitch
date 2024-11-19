##############################################################################################################################################
# 
# Firmware processing configuration. Most options are optional.
#
##############################################################################################################################################

#from kemper import KemperMappings, KemperEffectSlot

Config = {
    
    # Max. number of MIDI messages being parsed before the next switch state evaluation
    # is triggered. If set to 0, only one message is parsed per tick, which leads to 
    # flickering states sometimes. If set too high, switch states will not be read for too long.
    # A good value is the maximum amount of switches. Default is 10.
    #"maxConsecutiveMidiMessages": 10,

    # Clear MIDI buffer beofre starting processing.
    "clearBuffers": True,                 

    # Max. milliseconds until a request is being terminated and it is
    # assumed that the Kemper device is offline. Optional, default is 2 seconds.
    #"maxRequestLifetimeMillis": 2000,

    # Update interval, for updating the rig date (which triggers all other data to update when changed) (milliseconds)
    # and other displays if assigned. 200 is the default.
    #"updateInterval": 200,

    # Amount of bytes that must at least be free at the time processing starts (normally the program requires anther about
    # 10kB for character loading etc., default threshold for the warning is 15kB).
    #"memoryWarnLimitBytes": 1024 * 15,

    ## Development Options ###################################################################################################################

    # Optional, shows the effect slot names in the display labels for EffectEnableAction
    #"showEffectSlotNames": True,

    # Debug output is printed to serial console via USB. 
    # See https://learn.adafruit.com/welcome-to-circuitpython/advanced-serial-console-on-mac-and-linux 

    "debugStats": True,                              # Show info about runtime and memory usage periodically every update interval
    "debugStatsInterval": 2000,                      # Update interval for runtime statistics (also affects the performance dot, default is 
                                                      # the "updateInterval" option)
    "debugBidirectionalProtocol": True,              # Debug the bidirectional protocol, if any
    #"debugUnparsedMessages": True,                   # Shows all incoming MIDI messages which have not been parsed by the application.
    #"debugSentMessages": True,                       # Shows all sent messages
    #"excludeMessageTypes": [ "SystemExclusive" ],    # Types to excude from "debugUnparsedMessage"

    # When a ClientParameterMapping instance is set here, incoming messages for this mapping will be shown.
    #"debugMapping": KemperMappings.EFFECT_TYPE(KemperEffectSlot.EFFECT_SLOT_ID_B),

    # Explore Mode: Set this to True to boot into explore mode. This mode listens to all GPIO pins available
    # and outputs the ID of the last pushed one, and also rotates through all available NeoPixels. 
    # Use this to detect the switch assignments on unknown devices. Optional.
    #"exploreMode": True
}
