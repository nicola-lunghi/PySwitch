# MidiCaptain4Kemper
alternative firmware for MidiCaptain footswitches to interact with Kemper Profiler

This extension is set on original [PaintAudio firmware 3.5](https://cdn.shopify.com/s/files/1/0656/8312/8548/files/FW_MINI6_KPP_V3.51.zip?v=1711205983)

<h2>Installation</h2>
You need a connection from MIDI Capatain to your computer. This must be done like:

1. Connect Midi Captain with your computer via USB cable.
2. Press and hold swith 1 (first in top line) while you turn on you MIDI Captian.
You should now see your device as MIDICAPTAIN on your computer.

3. Than you can copy the files you want to add/change to the MIDI Captain device.
Here you have to copy the Python skript to the device folder /lib.
4. And than you have to manipulate the code.py in the root folder.

If you want have both possibilities (original SW and this skript), change code.py to:

	import board
	import time
	import digitalio
	
	switch2 = digitalio.DigitalInOut(board.GP25)
	switch2.direction = digitalio.Direction.INPUT
	switch2.pull = digitalio.Pull.UP
  
	print("Press Switch 2 to enter Kemper Stomp Modus")
	time.sleep(2)
  
	if switch2.value is False:
	 switch2.deinit()
	 import kemperstomp
	else:
	 switch2.deinit()
	 import midicaptain6s_kpp

Than you have two seconds while booting MIDI Captain to press the middle switch in the top row and enter the skript.

Otherwise the original firmware will be used.
