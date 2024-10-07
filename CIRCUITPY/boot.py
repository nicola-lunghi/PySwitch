import storage
import board
import digitalio
import time
import supervisor

############################################################################################

# Initializes a switch. Returns the switch instance.
def init_switch(pin):
	switch = digitalio.DigitalInOut(pin) 
	switch.direction = digitalio.Direction.INPUT
	switch.pull = digitalio.Pull.UP
	time.sleep(0.05)
	return switch

# Is a switch pressed? 
def is_switch_pressed(switch):
	return switch.value == False   # Inverse logic!

############################################################################################
 
# When this switch is pressed during boot, the USB drive will be mounted
switch_mount_usb = init_switch(board.GP1)       

# When this switch is pressed during boot, the autoreload feature will be enabled (rebooting on every drive change)
switch_autoreload = init_switch(board.GP25)     

# No USB drive in normal operation
if is_switch_pressed(switch_mount_usb) == False:
    storage.disable_usb_drive()

# No autoreload in normal operation
if is_switch_pressed(switch_autoreload) == False:
	supervisor.disable_autoreload()

############################################################################################


# Board Infos
# Raspberry Pi Pico (RP2040)
#
# GP0
# GP1  - FootSwitch 1
# GP2
# GP3
# GP4  bat_chg_led
# GP5
# GP6  charging
# GP7  NeoPixel
# GP8  asyncio PWMOut frequency
# GP9  - FootSwitch 3
# GP10 - FootSwitch 4
# GP11 
# GP12 tft_dc   (SPI1 RX)
# GP13 tft_cs   (Chip Select)
# GP14 spi_clk  (SPI1SCK)
# GP15 spi_mosi (SPI1 TX)
# GP16 Midi GP16GP17 baudrate
# GP17 Midi GP16GP17 baudrate
# GP18
# GP19
# GP20
# GP21
# GP22
# GP23
# GP24 
# GP25 - FootSwitch 2
# GP26
# GP27
# GP28
