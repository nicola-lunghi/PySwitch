# PySwitch MIDI Controller Firmware

This project provides an open source firmware for CircuitPy Microcontroller based MIDI controllers. It can control devices via MIDI based on a 
generic configuration script. Features are:

- Program (Foot)switches to send MIDI messages. Each switch can do multiple actions.
- Request parameters via NRPN MIDI from the controlled device and evaluate them on a TFT screen or using NeoPixel LEDs (for example the rig/amp/IR names can be displayed)
- Use conditions in the configuration to make functions depending on MIDI parameters of the device
- Define the device to be controlled via a custom python library, implementing base classes from the firmware

## Motivation

The firmware has been developed to interface the PaintAudio MIDI Captain series of MIDI controller pedals to the Kemper Profiler Player, which can be controlled
very deeply via MIDI. It is based on the great work of @gstrotmann who did the hardware reverse engineering and provided the initial script this project is based on (https://github.com/gstrotmann/MidiCaptain4Kemper).

The manufacturer PaintAudio also provides a Kemper Player related firmware (<a href="https://cdn.shopify.com/s/files/1/0656/8312/8548/files/FW_MINI6_KPP_V3.51.zip?v=1711205983" target="_blank">PaintAudio firmware 3.5</a>) but this is hard wired all along, so it can only control few functions of the Player like enabling/disabling effect slots. 

This project is developed generically, so it can basically be run on any board which runs CircuitPy, using the Adafruit libraries to run a TFT display and LEDs, to control basically any device which is controlled in a similar way as the Kemper devices (it can also be used to control all other Kemper Profiler products, however his has not been tested and might need slight changes in the pyswitch_kemper module) and address
any parameter or other information the controlled device provides.

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
- **displays.py**: Defines the layout of the TFT display and which data to show

These files can make use of the objects contained in **kemper.py** which provide all necessary mappings for the Kemper devices. This is currently only tested with the Profiler Player, but the MIDI specification is the same for most parts. Additional functionality for the Toaster/Stage versions can be added in kemper.py later if needed. Note that for using other devices than the Player you have to adjust the NRPN_PRODUCT_TYPE value accordingly (which should be the only necessary change).

### Global configuration

The file **config.py** only defines one dict named Config, which by default is empty. Please refer to the comments in the file for details on the possible options, which are all optional.

### Switch Assignment

The file **switches.py** must provide two objects:

- **ValueProvider**: Must be an instance of a class which is capable of parsing MIDI messages for the client used. Use KemperMidiValueProvider (from kemper.py) to use the controller with Kemper devices:

```python
ValueProvider = KemperMidiValueProvider()
```

- **Switches**: Must be a list of switch definitions. A switch definitions consists of a dict with the following entries:
	- **"assignment"**: Assignment to the hardware switch and corresponding LED pixels. Must be a dict. You can specify this manually, however it is recommended to use the predefined assignments in lib/pyswitch/hardware/hardware.py. Must contain the following entries:

		- **"model"**: Instance capable of reporting a switch state (reading a board GPIO). Use AdafruitSwitch from lib/pyswitch/hardware/adafruit.py
		
		- **"pixels"**: Tuple of pixel indices assigned to the switch, for example (0, 1, 2) for the first three LEDs. NeoPixels are controlled by index, and for example the PaintAudio MIDICaptain devices feature three LEDs per switch which can be addressed separately.
		
		- **"name"**: Optional name for debugging output

	- **"actions"**: List of actions to be triggered by the switch, see below.

	- **"initialColors"**: Optional: Color initially set before any actions are being processed. If not set, random colors are set.

	- **"initialBrightness"**: Optional: Brightness initially being set before any actions are being processed. If not set, the default (1) is used.

#### Switch Actions

Example for assigning switch 1 of a MIDICaptain Nano 4 to switching the Kemper effect slot A on or off:

```python
Switches = [
	{
        "assignment": SwitchDefinitions.PA_MIDICAPTAIN_NANO_SWITCH_1,
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

- PushButtonModes.ENABLE: Switch the functionality on (always, no switching off again!)
- PushButtonModes.DISABLE: Switch the functionality off (always, no switching on again)
- PushButtonModes.LATCH: Toggle state on every button push
- PushButtonModes.MOMENTARY: Enable on push, disable on release
- PushButtonModes.MOMENTARY_INVERSE: Disable on push, Enable on release
- PushButtonModes.HOLD_MOMENTARY: Combination of latch, momentary and momentary inverse: If pushed shortly, latch mode is used. If pushed longer than specified in the "holdTimeMillis" parameter, momentary mode is used (inverse or not: This depends on the current state of the functionality. When it is on, it will momentarily be switched off and vice versa). This is the default for most of the actions.
- PushButtonModes.ONE_SHOT: Fire the SET command on every push (show as disabled)

Each switch can be assigned to any number of actions, which are implementing the functionality for the switch. Actions are instances based on the lib/pyswitch/controller/actions/Action base class. Normally you would use predefined actions as provided by kemper.py (class KemperActionDefinitions as used in the example above), however you could also directly use the classes defined in lib/pyswitch/controller/actions/actions.py and provide all the MIDI mapping manually.

##### Conditional Actions

Actions can also be defined depending on a parameter for example: Instead of a list of Action instances, "actions" can also be a Condition, for example the switch could be assigned to tapping tempo if the rig name contains the token "TAP", and control effect slot A if not:

```python
Switches = [
	{
        "assignment": SwitchDefinitions.PA_MIDICAPTAIN_NANO_SWITCH_1,
        "actions": [
            ParameterCondition(
                mapping = KemperMappings.RIG_NAME,
                mode = ParameterConditionModes.MODE_STRING_CONTAINS,
                ref_value = "TAP",

                yes = [
                    KemperActionDefinitions.TAP_TEMPO()
                ],

                no = [
                    KemperActionDefinitions.EFFECT_STATE(
                        slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A
                    )
                ]

            # ... Define further actions for switch 1 here
        ]
    },

    # ... Define further switches here
]
```

Note that conditions can be deeply nested: Any action in the yes or no branches can be a Condition itself! This example only assigns the tap tempo action if both the TAP token is contained in the rig name and slot DLY has a delay effect loaded:

```python
Switches = [
    {
        "assignment": SwitchDefinitions.PA_MIDICAPTAIN_NANO_SWITCH_1,
        "actions": [
            ParameterCondition(
                mapping = KemperMappings.RIG_NAME,
                mode = ParameterConditionModes.MODE_STRING_CONTAINS,
                ref_value = "TAP",

                yes = [
                    ParameterCondition(
                        mapping = KemperMappings.EFFECT_STATE(
                            KemperEffectSlot.EFFECT_SLOT_ID_DLY
                        ),
                        mode = ParameterConditionModes.MODE_EQUAL,
                        ref_value = 1,
						
                        yes = [
                            KemperActionDefinitions.TAP_TEMPO(
                                display = {
                                    "id": 123, 
                                    "index": 0,
                                    "layout": ACTION_LABEL_LAYOUT
                                }
                            )
                        ],

                        no = [
                            KemperActionDefinitions.EFFECT_STATE(
                                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A,
                                display = {
                                    "id": 123, 
                                    "index": 0,
                                    "layout": ACTION_LABEL_LAYOUT
                                }
                            )
                        ]
                    )
                ],

                no = [
                    KemperActionDefinitions.EFFECT_STATE(
                        slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A,
                        display = {
                            "id": 123, 
                            "index": 0,
                            "layout": ACTION_LABEL_LAYOUT
                        }
                    )
                ]
            ),

            # ... Define further actions for switch 1 here
        ]
    },

    # ... Define further switches here
]
```

Available condition types (see lib/pyswitch/controller/COnditionTree.py):
- **ParameterCondition**: Depends on a parameter. See implementation for available comparison modes.
- **PushButtonCondition**: Depends on the state of another switch

##### Display Labels for Actions

The last example only uses the switch LEDs to indicate the effect status (brightness) and type (color). You can also connect a display area (defined in **displays.py**) to the action, so the effect type (color and name) and state (brightness) are also visualized on screen:

```python
Switches = [
    {
        "assignment": SwitchDefinitions.PA_MIDICAPTAIN_NANO_SWITCH_1,
        "actions": [
            KemperActionDefinitions.EFFECT_STATE(
                slot_id = KemperEffectSlot.EFFECT_SLOT_ID_A,
                display = {
                    # Some arbitrary ID defined in displays.py
                    "id": 123,

                    # Only used when the display element is a split container, to 
                    # address the part of the display used  for this switch
					"index": 0,

                    # Mandatory: DisplayLabel Layout definition (see below)      
                    "layout": ACTION_LABEL_LAYOUT
                },
            )
        ]
    },

    #... Define further switches here
]
```

### TFT Display Layout Definition

The file **displays.py** must only provide a list of DisplayElement instances in a list named Displays:

```python
Displays = [        
    # Header area
    DisplaySplitContainer(
        id = 123,
        name = "Header",
        bounds = DisplayBounds(0, 0, 240, 40)  # x, y, width, height
    ),

    # Footer area
    DisplaySplitContainer(
        id = 456,
        name = "Footer",
        bounds = DisplayBounds(0, 200, 240, 40)  # x, y, width, height
    ),

    # Rig name
    ParameterDisplayLabel(
        name = "Rig Name",
        bounds = DisplayBounds(0, 40, 160, 40)  # x, y, width, height
        layout = {
            "font": "/fonts/PTSans-NarrowBold-40.pcf",
            "lineSpacing": 0.8,
            "maxTextWidth": 220,
        },
        parameter = {
            "mapping": KemperMappings.AMP_NAME,
            "depends": KemperMappings.RIG_DATE   # Only update this when the 
                                                 # rig date changed (optional)
        }        
    ),

    # ... Define further elements here
]
```

The areas are stacked in the defined order, elements defined down the list will overlap the upper ones. 

This example defines three display areas:

- A header and a footer, which are split elements: This means they can hold any amound of sub-elements to be used by actions by specifying the "index" parameter in their "display" configuration. Note that the layout definition in this case also comes from the "display" definition.

- A rig name display, which is a ParameterDisplay instance: This is a display label which shows a MIDI parameter, in this case the rig name. In this special case the "depends" entry specifies that the rig name shall be updated anytime the rig date changes.

All available area types are defined in lib/pyswitch/ui/elements/elements.py, see there for more details on parameters for the available types:

- **DisplayLabel**: Just a label showing text over a background. 
- **ParameterDisplayLabel**: DisplayLabel tied to a device parameter, which is shown and constantly updated (used for string parameter display)
- **DisplaySplitContainer**: Container element which can hold any amount of labels. The amount of labels is automatically determined by their usages in the switches.py file for example. 
- **PerformanceIndicator**: A small black dot getting red when the processing starts to lag (which can occur when too much stuff is configured)
- **StatisticsDisplayLabel**: A DisplayLabel showing processing statistics

#### Subtractive Layouting

You can specify the dimensions and positions of all display elements manually like in the example snippets above, but the DIsplayBounds class offers a far more elegant way to split up the available area. Just create an instance of it with all available space and then, in the Displays list, use it to "cut off" parts of it one after each other. 

The following snippets demonstrate this: The next two examples do exactly the same thing on a 240x240 screen (other parameters omitted for clarity):

```python
Displays = [ 
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
```

```python
# Create instance with all available space
bounds = DisplayBounds(0, 0, 240, 240)

Displays = [ 
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
```

See the DisplayBounds class in /lib/pyswitch/ui/elements/DisplayElement.py for more available methods.

#### Conditional layouts

The layout parameter for some types can also be a Condition (depending on a rig parameter for example) holding several layouts (also deeply, analog to the action conditions described above), for example to show some rig names with a different background or text color, like in this example:

```python
Displays = [ 
    # Rig name
    ParameterDisplayLabel(
        name = "Rig Name",
        bounds = DisplayBounds(0, 0, 240, 240),   

        layout = ParameterCondition(
            mapping = KemperMappings.RIG_NAME,
            mode = ParameterConditionModes.MODE_STRING_CONTAINS,
            ref_value = "ORANGE",

            yes = {
                "font": "/fonts/PTSans-NarrowBold-40.pcf",
                "lineSpacing": 0.8,
                "maxTextWidth": 220,
                "backColor": Colors.BLACK
            },

            no =  {
                "font": "/fonts/PTSans-NarrowBold-40.pcf",
                "lineSpacing": 0.8,
                "maxTextWidth": 220,
                "backColor": Colors.ORANGE
            }
        ),

        parameter = {
            "mapping": KemperMappings.RIG_NAME,
            "depends": KemperMappings.RIG_DATE,
            "textOffline": "Kemper Profiler (offline)",
            "textReset": "Loading Rig..."
        }
    ),

    # ...
]
```

The rig name display will have an orange background when the rig name contains the word "ORANGE".

**NOTE**: Not all layout parameters can be changed freely. It is not possible to:
- Background color must be set either not at all for all possible condition branches, or set for all of them (use Colors.BLACK or (0, 0, 0) instead of no background).
- Corner radius cannot be changed.
- If one branch uses a stroke greater than zero, all of them must have a stroke greater than zero. Set the outline color to the same as the back color to workaround this.

### Mappings

#### General

The MIDI messages to set/request parameters from the device are bundled in Mappings. A mapping (see class ClientParameterMapping) can contain the following:
- SET message: MIDI message to be used to set the parameter (value will be overridden with the real value before sending)
- REQUEST message: MIDI message to request the parameter from the device
- RESPONSE message: MIDI message template to be used to compare incoming MIDI messages to. Defines how the device returns the value requested.

See the ClientParameterMapping class for deeper details.

#### Kemper Mappings

The file **kemper.py** contains predefined mappings to be used in the switches and displays configurations. These include the most usual parameters already, if you need more than that you can either define them manually or add new mappings to kemper.py (recommended).

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
                                
    # Corner radius for the background (optional: default is 0). 
    # Should be used sparingly because it takes a lot of memory!
    "cornerRadius": 0,          

    # Ouline stroke (optional, default is 0). Width of the 
    # optional outline
    "stroke":                   
                                
    # Initial text (default is None).
    "text": "Initial Text"      
}
```

## Development

The sources are all contained in the lib/pyswitch module, which has the following basic structure:

```
/lib/pyswitch/
    controller/
    hardware/
    ui/
```

- **controller** contains the main application logic
- **hardware** provides access to the adafruit hardware
- **ui** contains the uiser interface shown on the TFT display

the Controller class in the **controller** folder represents the main application controller class which initiates the processing loop. It is used in the code.py file as follows (irrelevant things omitted for clarity):

```python
from pyswitch.hardware.adafruit import AdafruitST7789DisplayDriver, AdafruitNeoPixelDriver, AdafruitFontLoader
from pyswitch.ui.UserInterface import UserInterface
from pyswitch.controller.Controller import Controller

# Initialize Display first to get console output on setup/config errors (for users who do not connect to the serial console)
display_driver = AdafruitST7789DisplayDriver()
display_driver.init()

# Load global config
from config import Config

# NeoPixel driver 
led_driver = AdafruitNeoPixelDriver()

# Buffered font loader
font_loader = AdafruitFontLoader()

# Create User interface
gui = UserInterface(display_driver, font_loader)

# Load configuration files
from displays import Displays
from switches import Switches, ValueProvider

# Controller instance (runs the processing loop and keeps everything together)
appl = Controller(led_driver, Config, ValueProvider, Switches, Displays, gui)
appl.process()
```

For each switch definition, an instance of FootSwitchController is created, which manages the actions provided by the Swiches list.

### Processing Loop

The main processing loop runs as follows (see Controller.process()):

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

All things which need to be updated regularily like Actions (to get current states from the Kemper) or display elements listening to parameters (ParameterDisplayLabel) are registered to the controller instance using add_updateable(), so in the update() method of Controller, all registered Updateables are updated.

### Actions

All actions inherit from the Action bas class. This class provides functionality used by all actions:

- Setting color and brightness of the switch LED(s): If a switch contains multiple actions which want to use the LEDs of the switch (self._use_switch_leds is set to True), the LEDs are assigned to each action. The rules are:
    - If only one action wants to set the LED(s), all three LEDs are used for that action.
	- If two actions use the LEDs, one will get LED 1+2 and the other will get LED 3.
	- If three actions use the LEDs, each action gets one LED.
	- If more than three actions exist, only the first three can use LEDs, the others will not show any LED status.

	*NOTE: This describes the behaviour for three LEDs per Switch, however also other amounts can be addressed. This depends on the "pixels" definitions in the port assignments.*

- Creates the display labels if the action has a display configuration

To create new, custom actions, just inherit Actions and implement the base methods as you wish:

- **init(self, appl, switch)**: Called before the processing loop ist started, and gives us references to the Controller (appl) and the switch (FootSwitchController). In the constructor of actions, no access to hardware (LEDs, display) is possible, so implement everything related to these thing in init() instead. **NOTE: Don't forget to call super().init()!**

- **do_update(self)**: This is called in the update intervals (see Processing Loop). Normally used to request parameter values from the Kemper to keep states up to date. *NOTE: Do NOT override update() directly!*

- **push(self)**: Called when the switch has been pushed down

- **release(self)**: Called when the switch has been released again

- **update_displays(self)**: Called after the enabled state of the action has been changed, to reflect that in the display/LEDs

- **force_update(self)**: Must reset all action states so the instance is being updated

- **reset_display(self)**: Must reset the displays and LEDs

Action provides the following properties to be used in child classes:

- **uses_switch_leds**: Boolean. Set this to true in your constructor if the action intends to use the LEDs.

- **enabled**: Boolean. Represents if the action is enabled or disabled (per Condition for example)

These properties can be used everywhere except in the constructor:

- **appl**: Reference to the Controller instance

- **switch**: Reference to the switch controller instance

- **label**: DisplayLabel instance bound to the action, if a display definition has been passed when creating it. If no display is set, this is None. Can be directly used to set the label text/color(s) etc.

- **debug**: Boolean. Will be True when debugging actions is enabled in config.py

#### PushButtonAction

For most things, we need the push/release states of the hardware switches to be interpreted as latch/momentary etc., so for those we have the PushButtonAction base class which can be run in several modes (usable in all actions derived from it).

This class implements the push and release methods and provides a **state** property. After changing this property, update_displays is called, so you can react to state changes there.

### Parameter Request Handling

The Client class executes all MIDI calls. 

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
    pass

# Called when the client is offline (requests took too long)
def request_terminated(self, mapping):
    pass
```

Internally, for each request a ClientRequest instance is created. If a mapping is requested which is already waiting, the listener is just added to the existing request. After the value has been received, all listeners are notified.

#### Value Provider

For parsing the incoming messages, a value provider class is used, defined in the switches.py file. This has to be implemented for each controlled device. For Kemper devices, the KemperMidiValueProvider class is located in kemper.py.

Value providers have to provide those two methods, which are device specific:

```python
# Must parse the incoming MIDI message and return the value contained.
# If the response template does not match, must return None.
# Must return True to notify the listeners of a value change.
def parse(self, mapping, midi_message):
    return False
    
# Must set the passed value on the SET message of the mapping.
def set_value(self, mapping, value):
    pass
```

## Explore Mode: Discover unknown IO Ports

The firmware is capable of running on several controllers, even if it has been developed on the PaintAudio MIDICaptain Nano 4. The definitions in hardware.py provide the hardware mappings for known devices (the MC Mini mapping comes from the original script from @gstrotmann):

```python
class SwitchDefinitions:

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

The Memory.watch() function can be placed wherever you need a measurement. It reports how much memory has been allocated since the last call, as well as how much is left.

### Debug Performance Issues

If you notify the device does not react sometimes when a switch is pressed, it might be that some action is taking much CPU. YOu can monitor the processing loop tick time by adding the following to your Displays list:

```python
Displays = [
	# ...
	
	StatisticalDisplays.STATS_DISPLAY(bounds)
]
```

This shows a display label with the max. and average tick times, as well as free memory, updated every second.

For less invasive measurement, there is also an element showing a small black dot which gets red when tick time gets over the update interval:

```python
Displays = [
	# ...
	
	StatisticalDisplays.STATS_DISPLAY(parent_bounds)
]
```

(This will not fill the entire bounds passed but be placed at the top right corner)

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
