# PySwitch MIDI Controller Firmware

This project provides a custom firmware for CircuitPy Microcontroller based MIDI controllers. It can control devices via MIDI based on a 
generic configuration script. Features are:

- Program (Foot)switches to send MIDI messages. Each switch can do multiple actions.
- Request parameters via NRPN MIDI from the controlled device and evaluate them on a TFT screen or using NeoPixel LEDs (for example the rig/amp/IR names can be displayed)
- Use conditions in the configuration to make functions depending on MIDI parameters of the device
- Define the device to be controlled via a custom python library, implementing base classes from the firmware

## Motivation

The firmware has been developed to interface the PaintAudio MIDI Captain series of MIDI controller pedals to the Kemper Profiler Player, which can be controlled
very deeply via MIDI. It is based on the great work of gstrotmann who did the hardware reverse engineering and provided the initial script this project is based on (https://github.com/gstrotmann/MidiCaptain4Kemper).

The manufacturer PaintAudio also provides a Kemper Player related firmware ([PaintAudio firmware 3.5](https://cdn.shopify.com/s/files/1/0656/8312/8548/files/FW_MINI6_KPP_V3.51.zip?v=1711205983)) but this is hard wired all along, so it can only control few functions of the Player like enabling/disabling effect slots. This project is developed generically, so it can basically be run on any board which runs CircuitPy, using the Adafruit libraries to run a TFT display and LEDs, to control basically any device which is controlled in a similar way as the Kemper devices (it can also be used to control all other Kemper Profiler products, however his has not been tested and might need slight changes in the pyswitch_kemper module) and address
any parameter or other information the controlled device provides.

## Installation

- Connect you device to your computer via USB and power it up. For PaintAudio MIDICaptain controllers, press and hold switch 1 while powering up to tell the controller to mount the USB drive.
- On your computer, you should now see the USB drive of the device (named MIDICAPTAIN for Paintaudio controllers, CIRCUITPY for generic boards)
- Delete the whole content of the USB drive. For PaintAudio devices, dont forget to save the contents on your hard drive (especially the license folder) if you perhaps want to restore the original manufacturer firmware later.
- Put the contents of the CIRCUITPY folder of the project on your device drive (named MIDICAPTAIN or CIRCUITPY).

## Startup Options

When the controller device is powered up with the pyswitch firmware installed, you have the following options:
- Press and hold switch 1 to mount the USB drive. Per default, this is disabled to save resources during normal operation.
- Press and hold switch 2 to enable auto-reload (obly valid when the USB drive is enabled). This enables re-booting the device whenever the USB drive 
contents have been changed (which is the default behaviour for CircuitPy boards). You could use this when configuring the firmware, so you can test your changes immediately, however if you connect the serial console in a terminal, you can control the reloading there with CTRL-D (see https://learn.adafruit.com/welcome-to-circuitpython/advanced-serial-console-on-mac-and-linux)

## Configuration

The whole configuration is done in the file lib/pyswitch/config.py which must define a python dictionary called Config. Here an example for the basic structure:

```python
Config = {
    "switches": [
		# Define switch assignments
	],
	"displays": [
		# Define TFT display areas
	]
}
```

- **"switches"** defines the actions to be triggered when a switch is pressed or held. It has to be an array of action definitions.



### Switch assignment

switches.py

#### Hardware assignment
#### Actions
#### Conditions

### TFT Display assignment

#### Display areas
#### Statistics options

## Development

### Modules

#### Main module

##### Actions
##### User Interface (for TFT displays)

#### Kemper interfacing module


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
