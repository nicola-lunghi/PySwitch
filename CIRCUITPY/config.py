##############################################################################################################################################
# 
# Firmware processing configuration. Most options are optional.
#
##############################################################################################################################################

from kemper import KemperMidiValueProvider

Config = {
    
    # Value provider which is responsible for setting values on MIDI messages for value changes, and parse MIDI messages
    # when an answer to a value request is received.
    "valueProvider": KemperMidiValueProvider(),

    # Max. number of MIDI messages being parsed before the next switch state evaluation
    # is triggered. If set to 0, only one message is parsed per tick, which leads to 
    # flickering states sometimes. If set too high, switch states will not be read for too long.
    # A good value is the maximum amount of switches. Default is 10.
    #"maxConsecutiveMidiMessages": 10,

    # Selects the MIDI channel to use [1..16] default is 1
    #"midiChannel": 1,

    # Max. milliseconds until a request is being terminated and it is
    # assumed that the Kemper device is offline. Optional, default is 2 seconds.
    #"maxRequestLifetimeMillis": 2000,

    # MIDI buffer size (60 is default)
    #"midiBufferSize": 60,

    # Update interval, for updating the rig date (which triggers all other data to update when changed) (milliseconds)
    # and other displays if assigned. 200 is the default.
    #"updateInterval": 200,

    ## Development Options ###################################################################################################################

    # Optional, shows the effect slot names for EffectEnableAction
    #"showEffectSlotNames": True,

    # Debug mode, optional. Shows verbose console output. You can listen to that on the serial port via USB on your computer,
    # see https://learn.adafruit.com/welcome-to-circuitpython/advanced-serial-console-on-mac-and-linux 
    #"debug": True,

    #"debugUserInterfaceStructure": True,             # Show UI structure after init 
    #"debugDisplay": True,                            # Show verbose messages from the display elements. Optional.
    #"debugActions": True,                            # Show verbose messages from actions. Optional.
    #"actionsDebugSwitchName": "1",                   # Optional, can be set to a switch assignment name (see Ports in definition.py)
                                                      # to only show action messages for the switch mentioned
    #"debugSwitches": True,                           # Show verbose output for switches (color, brightness) or a switches 
                                                      # actions are triggered. Optional.
    #"debugParameters": True,                         # Show messages from the global parameter controller
    #"debugClient": True,                             # Show all requests and responses to/from the Kemper Profiler. Optional.
    #"clientDebugMapping": KemperMappings.NEXT_BANK,  # Optional, if set the kemper classes will only output messages related to
                                                      # the specified mapping.
    #"debugClientRawMidi": True,                      # Debug raw kemper MIDI messages. Only regarded whe "debugKemper" is enabled, too.
    #"debugMidi": True,                               # Debug Adafruit MIDI controller. Normally it is sufficient and more readable 
                                                      # to enable "debugKemperRawMidi" instead, which also shows the MIDI messages sent
                                                      # and received. Optional.
    #"debugConditions": True,                         # Debug condition evaluation

    # Set this to True to boot into explore mode. This mode listens to all GPIO pins available
    # and outputs the ID of the last pushed one, and also rotates through all available NeoPixels. 
    # Use this to detect the switch assignments on unknown devices. Optional.
    #"exploreMode": True
}
