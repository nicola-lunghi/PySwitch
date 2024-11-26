# PySwitch MIDI Controller Firmware

This project provides an open source firmware for CircuitPy Microcontroller based MIDI controllers. It can control devices via MIDI based on a 
generic configuration script. Features are:

- Program (Foot)switches to send MIDI messages. Each switch can do multiple actions.
- Request parameters via NRPN MIDI from the controlled device and evaluate them on a TFT screen or using NeoPixel LEDs (for example the rig/amp/IR names can be displayed)
- Establish a bidirectional communication with the client device (implemented for the Kemper Profiler Player, but can be used for anything with similar protocol)
- Use callbacks in the configuration to make functions depending on MIDI parameters of the device, or program any other custom behaviour
- Ready-to-go Device implementation for the Kemper Profiler Player (R), others can be added
- MIDI routing capatbilities

![Overview Image](https://github.com/user-attachments/assets/c48903b2-a5f7-4d78-b7eb-9fca98dbfbe0)

## Motivation

The firmware has been developed to interface the PaintAudio MIDI Captain series of MIDI controller pedals to the Kemper Profiler Player, which can be controlled very deeply via MIDI. It is based on the great explorational work of @gstrotmann who did the hardware reverse engineering and provided the initial script this project is based on (https://github.com/gstrotmann/MidiCaptain4Kemper).

The manufacturer PaintAudio also provides a Kemper Player related firmware (<a href="https://cdn.shopify.com/s/files/1/0656/8312/8548/files/FW_MINI6_KPP_V3.51.zip?v=1711205983" target="_blank">PaintAudio firmware 3.5</a>) but this is hard wired all along, so it can only control few functions of the Player like enabling/disabling effect slots. 

This project is developed generically, so it can basically be run on any board which runs CircuitPy, using the Adafruit libraries to run a TFT display and LEDs, to control basically any device which is controlled in a similar way as the Kemper devices (it can also be used to control all other Kemper Profiler products, however his has not been tested and might need slight changes in the pyswitch_kemper module) and address any parameter or other information the controlled device provides. You just have to provide the apropriate adapter classes and mappings!

## Installation

1. Connect you device to your computer via USB and power it up. For PaintAudio MIDICaptain controllers, press and hold switch 1 while powering up to tell the controller to mount the USB drive.
2. On your computer, you should now see the USB drive of the device (named MIDICAPTAIN for Paintaudio controllers, CIRCUITPY for generic boards)
3. Delete the whole content of the USB drive. For PaintAudio devices, dont forget to save the contents on your hard drive (especially the license folder) if you perhaps want to restore the original manufacturer firmware later.
4. Copy everything in the "content" folder of the project to the root folder on your device drive (named MIDICAPTAIN or CIRCUITPY).

## Startup Options

When the controller device is powered up with the pyswitch firmware installed, you have the following options:
- Press and hold switch 1 to mount the USB drive. Per default, this is disabled to save resources during normal operation.
- Press and hold switch 2 to enable auto-reload (obly valid when the USB drive is enabled). This enables re-booting the device whenever the USB drive 
contents have been changed (which is the default behaviour for CircuitPy boards). You could use this when configuring the firmware, so you can test your changes immediately, however if you connect the serial console in a terminal, you can control the reloading there with CTRL-D (see <a href="https://learn.adafruit.com/welcome-to-circuitpython/advanced-serial-console-on-mac-and-linux" target="_blank">this tutorial</a>)

## Configuration

The whole configuration is done in some files in the root directory (of the device drive). These are all python scripts and follow the corresponding syntax rules. 

*Technical note: The pyswitch module does not import any of the files in the root folder directly. The code.py script (which is the CircuitPy entry point) loads all configuration.*

- **config.py**: Global configuration (MIDI channel, processing control, debug switches)
- **switches.py**: Defines which action(s) are triggered when a switch is pushed
- **display.py**: Defines the layout of the TFT display and which data to show
- **communication.py**: Defines the communication with the client, as well as generic MIDI routing between available MIDI ports

These files can make use of the objects contained in **lib/pyswitch/clients/kemper.py** which provide all necessary mappings for the Kemper devices. This is currently only tested with the Profiler Player, but the MIDI specification is the same for most parts. Additional functionality for the Toaster/Stage versions can be added in kemper.py later if needed. Note that for using other devices than the Player you have to adjust the NRPN_PRODUCT_TYPE value accordingly (which should be the only necessary change). Contributors welcome!

### Global configuration

The file **config.py** only defines one dict named Config, which by default is empty. Please refer to the comments in the file for details on the possible options, which are all optional.

### MIDI Communication Setup

The **communication.py** file defines the handling of MIDI. This includes the MIDI routing. It must contain a Communication dictionary like follows:

```python

_USB_MIDI = MidiDevices.PA_MIDICAPTAIN_USB_MIDI(
    in_channel = None,  # All channels will be received
    out_channel = 0     # Send on channel 1
)

Communication = {

    # MIDI setup. This defines all MIDI routings. You at least have to define routings from and to 
    # the MidiController.PYSWITCH source/target or the application will not be able to communicate!
    "midi": {
        "routings": [
            # Application: Receive MIDI messages from USB
            MidiRouting(
                source = _USB_MIDI,
                target = MidiController.APPLICATION
            ),

            # Application: Send MIDI messages to USB
            MidiRouting(
                source = MidiController.APPLICATION,
                target = _USB_MIDI
            ),
        ]
    }
}
```

- "midi": Configuration for the MidiController. This is a flexible MIDI routing class which can be configured using a list of MidiRouting instances, each defining one route (in one direction only). The example above defines the minimal necessary routings to run the application. If you do not provide any routings, the application will not be able to communicate to the outer world. 

##### MIDI Routings

A routing has a source and a target, both of which must be instances being able to send and receive MIDI messages. You can use:
- Adafruit's own MIDI handler (adafruit_midi.MIDI)
- The wrappers AdfruitUsbMidiDevice (for USB MIDI) and AdfruitDinMidiDevice (for DIN MIDI) (recommended) which are also used in the example above (wrapped again by MidiDevices, see the source code there)
- The constant MidiController.APPLICATION. This represents the application itself.

This example will, in addition to normal operation as in the last example, also pass all data from DIN Input to USB output (MIDI Through):

```python

# Pre-define all needed MIDI devices here in advance 
# (multiple creation would waste memory)
_DIN_MIDI = MidiDevices.PA_MIDICAPTAIN_DIN_MIDI(
    in_channel = None,  # All channels will be received
    out_channel = 0     # Send on channel 1
)

_USB_MIDI = MidiDevices.PA_MIDICAPTAIN_USB_MIDI(
    in_channel = None,  # All channels will be received
    out_channel = 0     # Send on channel 1
)

Communication = {

    # MIDI setup. This defines all MIDI routings. You at least have to define routings from and to 
    # the MidiController.PYSWITCH source/target or the application will not be able to communicate!
    "midi": {
        "routings": [
            # MIDI Through from DIN to USB
            MidiRouting(
                source = _DIN_MIDI,
                target = _USB_MIDI
            ),

            # Application: Receive MIDI messages from USB
            MidiRouting(
                source = _USB_MIDI,
                target = MidiController.APPLICATION
            ),

            # Application: Send MIDI messages to USB
            MidiRouting(
                source = MidiController.APPLICATION,
                target = _USB_MIDI
            ),
        ]
    }
}
```

It is also possible to either route multiple sources to one target or vice verse, to distribute or merge messages. 
The examples also contains samples for setting up MIDICaptain USB and DIN communication as well as MIDI through, or connecting the application to DIN and/or USB MIDI.

**NOTE**: Not all message types are forwarded by default to save memory, only the message types needed for the Kemper devices are enabled:
- ControlChange
- ProgramChange
- SystemExclusive

There are several other types defined in the <a href="https://docs.circuitpython.org/projects/midi/en/latest/" target="_blank">>adafruit_midi library</a>. If you need them to be processed, see file lib/pyswitch/hardware/adafruit.py and add the message types you need in the import section at the top (importing the types is sufficient, no further code changes needed). For types not listed (like MIDI Clock) these can be defined manually, see comments.

#### Bidirectional Communication

Some clients like the Kemper devices support a bidirectional communication mode. This wording is a bit misleading because the PySwitch application can react to changes of the client also if this mode is not enabled. However, bidirectional mode will greatly reduce MIDI traffic and improve reaction delays, and for example the Tuner note and deviation infos necessary for the tuner display (see below) are just sent in bidirectional mode, so this is the preferred mode of operation and enabled by default in all examples.

See this chart for some differences between the operation modes:

|                                             | **Non-Bidirectional** | **Bidirectional**    |
|---------------------------------------------|-----------------------|----------------------|
| Reflect changes on the client               | Yes                   | Yes                  |
| Parameter values are requested periodically | Yes                   | No (\*)              |
| Tuner information available                 | No                    | Yes (Note and dev.)  |
| Tempo Messages (for synced blinking LEDs)   | No                    | Yes                  |

*(\*) Bidirectional mode is not available for all parameters. However, you do not need to specify this, the **lib/pyswitch/clients/kemper.py** file contains the definitions looked up by the application.*

To enable bidirectional communication, you have to provide a suitable protocol implementation (instance of BidirectionalProtocol) to the Communication object like follows, using the Kemper specific implementation from **lib/pyswitch/clients/kemper.py**:

```python
Communication = {

    # Optional: Protocol to use. If not specified, the standard Client protocol is used which requests all
    # parameters in each update cycle. Use this to implement bidirectional communication.
    "protocol": KemperBidirectionalProtocol(
        time_lease_seconds = 30               # When the controller is removed, the Profiler will stay in bidirectional
                                              # mode for this amount of seconds. The communication is re-initiated every  
                                              # half of this value. 
    ),

    # ...
}
```

### Switch Assignment

The file **switches.py** must provide a Switches list holding all switch assignments. A switch definitions consists of a dict with the following entries:
	
- **"assignment"**: Assignment to the hardware switch and corresponding LED pixels. Must be a dict. You can specify this manually, however it is recommended to use the predefined assignments in lib/pyswitch/hardware/hardware.py. Must contain the following entries:

    - **"model"**: Instance capable of reporting a switch state (reading a board GPIO). Use AdafruitSwitch from lib/pyswitch/hardware/adafruit.py
    
    - **"pixels"**: Tuple of pixel indices assigned to the switch, for example (0, 1, 2) for the first three LEDs. NeoPixels are controlled by index, and for example the PaintAudio MIDICaptain devices feature three LEDs per switch which can be addressed separately.
    
    - **"name"**: Optional name for debugging output

- **"actions"**: List of actions to be triggered by the switch, see below.

#### Switch Actions

Example for assigning switch 1 of a MIDICaptain Nano 4 to switching the Kemper effect slot A on or off:

```python
Switches = [
	{
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_1,
        "actions": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A
            ),

            # ... Define further actions for switch 1 here
        ]
    },

    # ... Define further switches here
]
```

##### Pushbutton Modes

Most actions feature a "mode" parameter. This parameter controls the behaviour of the switch as defined here:

- **PushButtonModes.ENABLE**: Switch the functionality on (always, no switching off again!)
- **PushButtonModes.DISABLE**: Switch the functionality off (always, no switching on again)
- **PushButtonModes.LATCH**: Toggle state on every button push
- **PushButtonModes.MOMENTARY**: Enable on push, disable on release
- **PushButtonModes.MOMENTARY_INVERSE**: Disable on push, Enable on release
- **PushButtonModes.HOLD_MOMENTARY**: Combination of latch, momentary and momentary inverse: If pushed shortly, latch mode is used. If pushed longer than specified in the "holdTimeMillis" parameter, momentary mode is used (inverse or not: This depends on the current state of the functionality. When it is on, it will momentarily be switched off and vice versa). This is the default for most of the actions.
- **PushButtonModes.ONE_SHOT**: Fire the SET command on every push (show as disabled)

Each switch can be assigned to any number of actions, which are implementing the functionality for the switch. Actions are instances based on the lib/pyswitch/controller/actions/Action base class. Normally you would use predefined actions as provided by lib/pyswitch/clients/kemper.py (class KemperActionDefinitions as used in the example above), however you could also directly use the classes defined in lib/pyswitch/controller/actions/actions.py and provide all the MIDI mapping manually.

##### Action Colors

Most actions provide a color option: If set, this defines the color for switch LEDs and an eventual display label. For example, the following example creates a rotary speed selector shown in purple:

```python
Switches = [
	{
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_1,
        "actions": [
            KemperActionDefinitions.ROTARY_SPEED(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A,
                color = (180, 0, 120)    # (R, G, B)
            )
        ]
    }
]
```

##### Enable/Disable Actions by Callback

Actions can also be defined depending on a parameter or other stuff: For example the switch could be assigned to tapping tempo if the rig name contains the token "TAP", and control effect slot A if not. This is accomplished by defining a custom callback class to enable/disable actions:

```python
# Custom callback function
class _RigNameCallback(Callback):
    def __init__(self):
        Callback.__init__(self)

        # You have to define the attribute .mappings as a list of mappings on
        # which your callback depends. This is optional, if you do not need further
        # mappings, just leave that out. If specified, the callback is updated 
        # automatically whenever the parameter of the mapping changes.
        self.mappings = [KemperMappings.RIG_NAME()]

        self._mapping = self.mappings[0]  # Just for internal reference

    # For Action enable/disable callbacks, there must be a enabled(action) method. This has to
    # return True or False for the action passed. For finding your actions, the id is used,
    # as set below.
    def enabled(self, action):  
        rig_name = self._mapping.value

        if action.id == 10:
            # Show Tap when TAP is contained
            return "TAP" in rig_name
        elif action.id == 20:
            # Show Effect Enable for slot A when TAP is not contained
            return "TAP" not in rig_name
        
# Create an instance of the callback here and use it for all actions involved. 
# It is also possible to use multiple instances but this saves some memory.
_enable_callback = _EnableCallback()

# Both actions now get the same callback which switches their states.
Switches = [
	{
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_1,
        "actions": [
            KemperActionDefinitions.TAP_TEMPO(
                id = 10,
                callback = _enable_callback
            ),
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A,
                id = 10,
                callback = _enable_callback
            )
        ]
    },

    # ... Define further switches here
]
```

##### Display Labels for Actions

The last example only uses the switch LEDs to indicate the effect status (brightness) and type (color). You can also connect a display area (defined in **display.py**) to the action, so the effect type (color and name) and state (brightness) are also visualized on screen. This works by importing labels defined in **display.py** and pass them to the display attribute of the action(s):

```python
from display import DISPLAY_LABEL_X

Switches = [
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_1,
        "actions": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A,
                display = DISPLAY_LABEL_X,
            )
        ]
    },

    #... Define further switches here
]
```

See below how the labels are defined.

#### Actions on Long Press (Hold)

You can assign different actions to long pressing of switches. This is done using the HoldAction class, which takes actions assigned to short press and long press separately:

```python
Switches = [
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_1,
        "actions": [
            HoldAction({
                "actions": [
                    KemperActionDefinitions.EFFECT_STATE(
                        slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A
                    )
                ],
                "actionsHold": KemperActionDefinitions.BANK_UP(
                    #use_leds = False    # See Note
                )
            })                        
        ]
    },

    #... Define further switches here
]
```

Also see the examples if you get problems, there are some with HoldAction included.

*NOTE: The LEDs of the switch will be shared among the actions participated. If you want just one action to use all LEDs of a switch, you can switch the usage off for an action using the use_leds parameter, for example with the hold action, so only the normal action will use the LEDs.*

*NOTE: Do not assign the same display label to the actions, this does not make sense and will result in erratic output.*

#### Custom Callbacks for Actions

Besides the general pushbutton or hold mechanisms, all functionality of the actions is implemented in callbacks. This works similar to the Enable callbacks described above (the mapping definition is the same), but these callbacks have to provide different member functions. The basis of this is the PushButtonAction:

```python
from pyswitch.controller.callbacks import Callback

class CustomCallback(Callback):
    def __init__(self):
        Callback.__init__(self)

        self.mappings = [] # DAdd your needed mappings here or remove line
        
    # This is called then the state changed (on/off, according to the pushbutton and
    # eventually hold modes involved around the action).
    def state_changed_by_user(self, action):
        if action.state == True:
            # ... do something
        else:
            # ... do something

    # This is called to update the visual feedback (display and LEDs)
    # whenever state changed or a mapping has been updated with a new value
    def update_displays(self, action):
        # You can set the display label's properties.
        # Beware that the label can be None if no display
        # has been passed to the action!
        if action.label:
            action.label.back_color = Colors.RED
            action.label.text = "foo"

        # The LED segments can be set with special 
        # properties of the Action base class, which 
        # only control the segments assigned to the 
        # action (see above). 
        #
        # Note that setting the color will not change 
        # anything. You have to set the brightness after
        # for the changes to take effect (even if the 
        # brightness is already set).        
        action.switch_color = (255, 255, 255) # (r, g, b), [0..255]
        action.switch_brightness = 0.8        # [0..1]


Switches = [
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_1,
        "actions": [
            PushButtonAction({
                "callback": CustomCallback(),
                "display": # ...
            })                        
        ]
    }
```

#### Binary Parameter Actions

To simply switch a parameter in an on/off fashion with values for on and off etc., the BinaryParameterAction is provided (which itself is a callback like in the last chapter). This is used by most of the predefined Kemper action definitions internally. Here an example which switches the rotary speed fast/slow:

```python
Switches = [
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_1,
        "actions": [
            PushButtonAction({
                "callback": BinaryParameterCallback(
                    mapping = KemperMappings.ROTARY_SPEED(
                        slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A
                    ),
                    text = "Fast",
                    color = Colors.BLUE
                ),
                "useSwitchLeds": True,   # Must be set to enable the LEDs!
                "display": #....
            })
        ]
    }
]
```

### TFT Display Layout Definition

The file **display.py** must provide a callback instance which returns the screen content to show, possibly depending on mappings or other criteria. The callback must provide a get_root() method which must return the DisplayElement to show:

```python
from pyswitch.controller.callbacks import Callback

# Layout used for the action labels (only used here locally)
_ACTION_LABEL_LAYOUT = {
    "font": "/fonts/H20.pcf",
    "backColor": DEFAULT_LABEL_COLOR,
    "stroke": 1
}

# Labels to be used by **switches.py**
DISPLAY_HEADER_1 = DisplayLabel(layout = _ACTION_LABEL_LAYOUT)
DISPLAY_HEADER_2 = DisplayLabel(layout = _ACTION_LABEL_LAYOUT)
DISPLAY_FOOTER_1 = DisplayLabel(layout = _ACTION_LABEL_LAYOUT)
DISPLAY_FOOTER_2 = DisplayLabel(layout = _ACTION_LABEL_LAYOUT)


class _SplashCallback(Callback):
    def get_root(self):
        return HierarchicalDisplayElement(
            bounds = DisplayBounds(0, 0, 240, 240),
            children = [        
                # Header area
                DisplaySplitContainer(
                    bounds = DisplayBounds(0, 0, 240, 40),  # x, y, width, height
                    children = [
                        DISPLAY_HEADER_1,
                        DISPLAY_HEADER_2
                    ]
                ),

                # Footer area
                DisplaySplitContainer(
                    bounds = DisplayBounds(0, 200, 240, 40),  # x, y, width, height
                    children = [
                        DISPLAY_FOOTER_1,
                        DISPLAY_FOOTER_2
                    ]
                ),

                # Rig name
                DisplayLabel(
                    bounds = DisplayBounds(0, 40, 160, 40)  # x, y, width, height
                    layout = {
                        "font": "/fonts/PTSans-NarrowBold-40.pcf",
                        "lineSpacing": 0.8,
                        "maxTextWidth": 220,
                    },
                    callback = KemperRigNameCallback()    
                ),

                # ... Define further elements here
            ]
        )

Splashes = _SplashCallback()
```

The areas are stacked in the defined order, elements defined down the list will overlap the upper ones. 

This example defines three display areas:

- A header and a footer, which are split elements: This means they can hold any amound of sub-elements to be used by actions by specifying the "index" parameter in their "display" configuration. Note that the layout definition in this case also comes from the "display" definition.

- A rig name display

All available area types are defined in lib/pyswitch/ui/elements/elements.py, see there for more details on parameters for the available types:

- **DisplayLabel**: Just a label showing text over a background. 
- **DisplaySplitContainer**: Container element which can hold any amount of labels, with the dimensions of the children being automatically set.
- **PerformanceIndicator**: A small black dot getting red when the processing starts to lag (which can occur when too much stuff is configured)
- **BidirectionalProtocolState**: A small black dot showing the state of the bidirectional communication protocol (green/red)

Display of values (like rig name) is done via callbacks, see below chapters about DisplayLabel.

##### Tuner Display

For the most popular case of showing a tuner display when the device goes into tuner mode, there is a ready made callback:

```python
Splashes = TunerDisplayCallback(
    splash_default = HierarchicalDisplayElement(
        bounds = _display_bounds,
        children = [
            # ... Display elements for normal display go here
        ]
    )
)
```

![image](https://github.com/user-attachments/assets/f4ba454f-b8a2-403c-b6b0-962a80dc9137)

#### Subtractive Layouting

You can specify the dimensions and positions of all display elements manually like in the example snippets above, but the DIsplayBounds class offers a far more elegant way to split up the available area. Just create an instance of it with all available space and then, in the Displays list, use it to "cut off" parts of it one after each other. 

The following snippets demonstrate this: The next two examples do exactly the same thing on a 240x240 screen (other parameters omitted for clarity):

```python
HierarchicalDisplayElement(
    bounds = DisplayBounds(0, 0, 240, 240),
    children = [        
        # Header (top 40 pixels)
        DisplayLabel(bounds = DisplayBounds(0, 0, 240, 40)),

        # Footer (bottom 40 pixels)
        DisplayLabel(bounds = DisplayBounds(0, 200, 240, 40)),

        # Rig name (remaining space)
        DisplayLabel(bounds = DisplayBounds(0, 40, 240, 160))

        # Some other display (above footer, but overlapping 
        # the rig name area)
        DisplayLabel(bounds = DisplayBounds(0, 180, 240, 20))
    ]
)
```

```python
# Create instance with all available space
bounds = DisplayBounds(0, 0, 240, 240)

HierarchicalDisplayElement(
    bounds = bounds,
    children = [        
        # Header (remove top 40 pixels from bounds and 
        # use that area)
        DisplayLabel(bounds = bounds.remove_from_top(40)),

        # Footer (remove bottom 40 pixels from bounds and 
        # use that area)
        DisplayLabel(bounds = bounds.remove_from_bottom(40)),

        # Rig name (take remaining space (header and bottom 
        # have been cut off))
        DisplayLabel(bounds = bounds),

        # Some other display (above footer, but overlapping 
        # the rig name area, so we use bottom() which does 
        # not change the bounds)
        DisplayLabel(bounds = bounds.bottom(20)),
    ]
)
```

See the DisplayBounds class in /lib/pyswitch/ui/ui.py for more available methods.

### Mappings

The MIDI messages to set/request parameters from the device are bundled in Mappings. A mapping (see class ClientParameterMapping) can contain the following (each can be one instance or a list of instances):
- **set**: MIDI message(s) to be used to set the parameter (value will be overridden with the real value before sending)
- **request**: MIDI message(s) to request the parameter from the device. Only used for non-bidirectional mappings.
- **response**: MIDI message(s) template to be used to compare incoming MIDI messages to. Defines how the device receives the parameter value.

See the ClientParameterMapping class for deeper details.

#### Kemper Mappings

The file **lib/pyswitch/clients/kemper.py** contains predefined mappings to be used in the switches and displays configurations. These include the most usual parameters already, if you need more than that you can either define them manually or add new mappings to kemper.py (recommended).

#### DisplayLabel Layout Definition

Layouts for DisplayLabel and related types are defined as dict. Here is an example showing all possible options:

```python
example_layout = {
    # Path to the font in PCF format (mandatory). A lot of fonts are
    # available at https://github.com/adafruit/circuitpython-fonts
    "font": "/fonts/H20.pcf",   
                                
    # Maximum text width in pixels (optional) for wrapping text
    "maxTextWidth": 220,        

    # Line spacing (optional, default is 1)
    "lineSpacing": 1,           

    # Text color (default is None, which will derive a contrasting
    # color automatically)
    "textColor": (255, 120, 0),                               

    # Background color (default is None) Can be a tuple also to 
    # show a rainbow background with multiple colors, 
    # for example (Colors.GREEN, Colors.YELLOW, Colors.RED)
    "backColor": (30, 30, 30), 
                                
    # Ouline stroke (optional, default is 0). Width of the 
    # optional outline. The outline is only "faked" for sake of memory 
    # usage (just the background is reduced in size)
    "stroke": 1,
                                
    # Initial text (default is None).
    "text": "Initial Text"      
}
```

#### Display Label Callbacks

For example if you want to show some custom text or a parameter value in a display label independent of an action or switch, this can be used by passing a callback to DisplayLabel. See example "Freeze and Tap Tempo" for the PaintAudio MIDICaptain NANO 4 which includes a custom callback for showing the current amp name.

## Development

The sources are all contained in the lib/pyswitch module, which has the following basic structure:

```
/lib/pyswitch/
    clients/
    controller/
    hardware/
    ui/
```

- **controller** contains the main application logic
- **hardware** provides access to the adafruit hardware
- **ui** contains the uiser interface shown on the TFT display
- **clients** provides code specific to clients (like the Kemper devices). This code is not used in the library itself, but in your config files in the drive root. Further client implementations (for Helix or Quad Cortex devices maybe) can be added here. If you want to contribute an implementation, just create it in the drive root, make it work from there, then share it to others by either putting it into the clients folder and creating a pull request, or just send the file over to me and i will integrate it.

The Controller class in the **controller** folder represents the main application controller class which initiates the processing loop. It is used in the code.py file as follows (irrelevant things omitted for clarity):

```python
from pyswitch.hardware.adafruit import AdafruitST7789DisplayDriver, AdafruitNeoPixelDriver, AdafruitFontLoader
from pyswitch.controller.Controller import Controller
from pyswitch.controller.MidiController import MidiController
from pyswitch.ui.UiController import UiController

# Initialize Display first to get console output on setup/config errors (for users who do not connect to the serial console)
display_driver = AdafruitST7789DisplayDriver()
display_driver.init()

# Load global config
from config import Config

# NeoPixel driver 
led_driver = AdafruitNeoPixelDriver()

# Buffered font loader
font_loader = AdafruitFontLoader()

# Load configuration files (this is where the clients specific code is used)
from display import Splashes
from switches import Switches
from communication import Communication

# Controller instance (runs the processing loop and keeps everything together)
appl = Controller(
    led_driver = led_driver, 
    communication = Communication, 
    midi = MidiController(
        routings = Communication["midi"]["routings"]
    ),
    config = Config, 
    switches = Switches, 
    ui = UiController(
        display_driver = display_driver,
        font_loader = font_loader,
        splash_callback = Splashes
    )
)

appl.process()
```

For each switch definition, an instance of FootSwitchController is created, which manages the actions provided by the Swiches list.

### Processing Loop

The main processing loop runs as follows (only rough overview, there is more to it in Controller.process(), see source):

```python
while True:
    # Update all actions and display areas in periodic intervals
    if self.period.exceeded:
        self.update(round_robin = False)

    # Receive MIDI messages.
    cnt = 0
    while True:
        # Detect switch state changes
        self._process_switches()

        # Reveive the next available MIDI message from the 
        # MIDI input buffer
        midimsg = self._midi.receive()

        # Process the midi message (see Client class)
        self.client.receive(midimsg)

        # Only a certain amount of messages is 
        # processed at once to prevent lags.
        cnt = cnt + 1
        if not midimsg or cnt > self._max_consecutive_midi_msgs:
            break  
```

All things which need to be updated regularily like Actions (to get current states from the Kemper for parameters not in bidirectional mode) or display elements listening to parameters (ParameterDisplayLabel) are registered to the controller instance using add_updateable(), so in the update() method of Controller, all registered Updateables are updated.

### Actions

All actions inherit from the Action base class. This class provides functionality used by all actions:

- Setting color and brightness of the switch LED(s): If a switch contains multiple actions which want to use the LEDs of the switch (self._use_switch_leds is set to True), the LEDs are assigned to each action. The rules are:
    - If only one action wants to set the LED(s), all three LEDs are used for that action.
	- If two actions use the LEDs, one will get LED 1+2 and the other will get LED 3.
	- If three actions use the LEDs, each action gets one LED.
	- If more than three actions exist, only the first three can use LEDs, the others will not show any LED status.

	*NOTE: This describes the behaviour for three LEDs per Switch, however also other amounts can be addressed. This depends on the "pixels" definitions in the port assignments.*

#### PushButtonAction

For most things, we need the push/release states of the hardware switches to be interpreted as latch/momentary etc., so for those we have the PushButtonAction base class which can be run in several modes (usable in all actions derived from it).

This class implements the push and release methods and provides a **state** property. After changing this property, update_displays is called, so you can react to state changes there.

### Parameter Request Handling

The Client class executes all MIDI calls. The BidirectionalClient class adds bidirectional communication on top of this.

#### Register Parameter Mapping

When you want to use a mapping somewhere (as the actions do for example), you have to register all used mappings in advance. This is done by calling register():

```python
def register(self, mapping, listener):
```

This is only relevant for bidirectional mappings, however it is important because you do not know in advance which parameters will become bidirectional at some times (for example when the parameter set is changed), so all mappings should be registered before the bidirectional protocol is initialized.

#### Set Parameter Value

To set a value via MIDI, use the set() method:

```python
def set(self, mapping, value):
```

It expects a mapping instance and the value to be sent.

#### Request Parameter Value

Requesting via NRPN MIDI messages is done like follows:

1. Send a message telling the device that a parameter value should be sent
2. Wait for the answer message and parse it when it arrives

The request method is used for this:

```python
def request(self, mapping, listener):
```

This requests the parameter (sends the REQUEST message of the passed mapping). The passed listener is called when the answer message has arrived. It has to implement these methods:

```python
# Called by the Client class when a parameter request has been answered.
# The value received is already set on the mapping.
def parameter_changed(self, mapping):
    # IMPORTANT: Use mapping.value even if you have your 
    # copy of the mapping referenced somewhere! The clients may
    # have altered it in the process.
    print("Value received: " + repr(mapping.value))

# Called when the client is offline (requests took too long)
def request_terminated(self, mapping):
    pass
```

Bidirectional mappings do not request values but must be able to receive them. Best practice is to implement everything for both modes (call register(), and request values). The request message (even when request() is called) will only be sent if the mapping is not bidirectional.

Internally, for each parameter a ClientRequest instance is created and added to a list of open requests. This differs between the operation modes: 
- In bidirectional mode, requests for bidirectional parameters will be created on register() already and never die. 
- For non-bidirection mappings, the requests will be created when request() is called, and die when the value has been received.

Every incoming MIDI message will be parsed by all open requests. This is the lifetime of a request:

1. Created (either by calling client.request() for non-bidirectional mappings, or at time of calling register() for bidirectional ones)
   When a request for the same mapping comes in at this time, the listener is just added to the existing request.
2. When a value comes in (MIDI message):
    - Tell all listeners that the value has changed by calling parameter_changed() on each listener.
3. When the mapping is not bidirectional, the request will be set to finished, which will trigger the client to clean it up. When the mapping is bidirectional, the request will never be finished and stay forever to receive further values.

#### Client-Specific parsing

For parsing the incoming messages and setting values before sending messages, a child class of ClientParameterMapping has to be used. This has to be implemented for each controlled device. For Kemper devices, the KemperParameterMapping class is defined in kemper.py.

```python
class MyMapping(ClientParameterMapping):

    # Must parse the incoming MIDI message and set its value on the mapping.
    # If the response template does not match, must return False, and
    # vice versa must return True to notify the listeners of a value change.
    def parse(self, midi_message):
        return False    

    # Must set the passed value on the SET message of the mapping.
    def set_value(self, value):
        pass
```

You have to provide two methods, which are device specific. See the Kemper implementation for details.

## Explore Mode: Discover unknown IO Ports

The firmware is capable of running on several controllers, even if it has been developed on the PaintAudio MIDICaptain Nano 4. The definitions in hardware.py provide the hardware mappings for known devices (the MC Mini mapping comes from the original script from @gstrotmann):

```python
class Hardware:

    # PaintAudio MIDI Captain Nano (4 Switches)
    PA_MIDICAPTAIN_NANO_SWITCH_1 = { "model": AdafruitSwitch(board.GP1),  "pixels": (0, 1, 2), "name": "1" }
    PA_MIDICAPTAIN_NANO_SWITCH_2 = { "model": AdafruitSwitch(board.GP25), "pixels": (3, 4, 5), "name": "2"  }
    PA_MIDICAPTAIN_NANO_SWITCH_A = { "model": AdafruitSwitch(board.GP9),  "pixels": (6, 7, 8), "name": "A"  }
    PA_MIDICAPTAIN_NANO_SWITCH_B = { "model": AdafruitSwitch(board.GP10), "pixels": (9, 10, 11), "name": "B"  }

    # PaintAudio MIDI Captain Mini (6 Switches)
    PA_MIDICAPTAIN_MINI_SWITCH_1 = { "model": AdafruitSwitch(board.GP1),  "pixels": (0, 1, 2), "name": "1"  }
    PA_MIDICAPTAIN_MINI_SWITCH_2 = { "model": AdafruitSwitch(board.GP25), "pixels": (3, 4, 5), "name": "2"  }
    PA_MIDICAPTAIN_MINI_SWITCH_3 = { "model": AdafruitSwitch(board.GP24), "pixels": (6, 7, 8), "name": "3"  }
    PA_MIDICAPTAIN_MINI_SWITCH_A = { "model": AdafruitSwitch(board.GP9),  "pixels": (9, 10, 11), "name": "A"  }
    PA_MIDICAPTAIN_MINI_SWITCH_B = { "model": AdafruitSwitch(board.GP10), "pixels": (12, 13, 14), "name": "B"  }
    PA_MIDICAPTAIN_MINI_SWITCH_C = { "model": AdafruitSwitch(board.GP11), "pixels": (15, 16, 17), "name": "C"  }
```

To discover the GPIO wiring of unknown devices (like the other MIDICaptains for example), a separate mode is provided. This can be enabled in config.py:

```python
Config = {    
    # Set this to True to boot into explore mode. This mode listens to all GPIO pins available
    # and outputs the ID of the last pushed one, and also rotates through all available NeoPixels. 
    # Use this to detect the switch assignments on unknown devices. Optional.
    "exploreMode": True
}
```

This can be used to detect which switch is wired to which IO port, and also determine the LED indexing. 

![image](https://github.com/user-attachments/assets/fb213844-b7e8-41fc-8e4d-5dcb97717822)

### Detect IO Port Wiring

All available IO ports (as defined in the board module) the display shows a separate label. When any port is used (switch is pushed) the corresponding label will be highlighted, so the display always shows the IO assignment of the last pressed switch.

### Detect LED Indexing

This works the following way: The program highlights one triplet of LEDs at a time. The triplet highlighted can be increased/decreased with the switches:
	- Every odd switch (green) will decrease the highlighted indices
	- Every even switch (orange) will increase the highlighted indices

The currently highlighted LEDs (white) will be shown in the display below the GPIO labels, so you can read them out to create your own switch definitions. Please, if you do so, share your results! Just send me a message or create an issue, i will add all definitions to the hardware.py file.

NOTE: This mode is currently hard wired for three LEDs per footswitch. However, it also can deliver the needed information for other constellations with some interpretation.

### Debug RAM Issues

The MIDICaptain Nano 4 only has about 200kB of available RAM. This is not much, especially because the display elements take much space. When creating more advanced display layouts, you might run into an error telling that no more memory can be allocated. 

The program provides some rudimentary memory monitoring. Enable this by uncommenting a line in code.py:

```python
...

from pyswitch.misc import Tools, Memory
Memory.start(zoom = 10)                  # <-- Uncomment this line

...
```

The program will report the allocations of memory on console like this:

```
code.py output:
............................................................ Starting with 187.1 KiB of 203.1 KiB                           XXXXXXXXXXXXXX.
Controller: Showing UI ..................................... Allocated 95.6 KiB     <<<<<<<|....... -> 91.6 KiB        45%  XXXXXXX........
Controller: Starting loop .................................. Allocated 37.9 KiB     <<<<<<<|....... -> 53.7 KiB        26%  XXXX...........
```

Every time memory is allocated or released, another message will be generated.

### Debug Performance Issues

If you notify the device does not react immediately sometimes when a switch is pressed, it might be that some action is taking much CPU. You can monitor the processing loop tick time by enabling the "debugStats" option in **config.py**.

### Unit Testing

All code in the content/lib/pyswitch folder is unit tested to a coverage of > 90%, which is important because this is a tool used in performances, so stability is a must. The test code is organized in the test folder of the project:

```
/content
/test
    /pyswitch         # Test code (test cases and mocks etc.)
    compose.yaml      # Config for docker compose to provide the test environment
    docker-run        # Runner script which starts the docker container and ssh into it
    Dockerfile        # Docker image (based on the official python image, but adds support for coverage.py)
    run               # Shell script to run tests (to be called in the docker terminal created by docker-run)
```

For running the tests, first run the container. From the project folder, run these commands in a shell:

```console
cd test
./docker-run
```

The docker image is built, the container is started and you get a prompt from a bash session inside the container. There, run the tests:

```console
/project/test/run
```

This should give you a result like this:

```console
a8545571c033:/# /project/test/run 
..................................................................................................................................................................................................
----------------------------------------------------------------------
Ran 194 tests in 0.159s

OK
Wrote HTML report to /project/test/report/index.html
```

You should find a coverage report in the test/report folder like this:

![image](https://github.com/user-attachments/assets/c539aaad-704a-44b5-9408-2f19c8d4da67)

## License

(C) Thomas Weber 2024 tom-vibrant@gmx.de

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
