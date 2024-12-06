#################################################################################################################################
# 
# Addressing definitions for some known devices. This helps addressing the different hardware I/O. Only change this when either
# one of the supported devices has been updated or new devices are added.
#
#################################################################################################################################
 
import board
from usb_midi import ports

from .adafruit import AdafruitSwitch, AdfruitDinMidiDevice, AdfruitUsbMidiDevice

#################################################################################################################################

# This provides known device definitions, ready to use in the config file.
class Hardware:

    # PaintAudio MIDI Captain Nano (4 Switches)
    # Board Infos
    # Raspberry Pi Pico (RP2040)
    #
    # GP1  - FootSwitch 1
    # GP4  bat_chg_led
    # GP6  charging
    # GP7  NeoPixel
    # GP8  asyncio PWMOut frequency
    # GP9  - FootSwitch A
    # GP10 - FootSwitch B
    # GP12 tft_dc   (SPI1 RX)
    # GP13 tft_cs   (Chip Select)
    # GP14 spi_clk  (SPI1SCK)
    # GP15 spi_mosi (SPI1 TX)
    # GP16 Midi GP16GP17 baudrate
    # GP17 Midi GP16GP17 baudrate
    # GP25 - FootSwitch 2
    PA_MIDICAPTAIN_NANO_SWITCH_1 = { "model": AdafruitSwitch(board.GP1),  "pixels": (0, 1, 2), "name": "1" }
    PA_MIDICAPTAIN_NANO_SWITCH_2 = { "model": AdafruitSwitch(board.GP25), "pixels": (3, 4, 5), "name": "2"  }
    PA_MIDICAPTAIN_NANO_SWITCH_A = { "model": AdafruitSwitch(board.GP9),  "pixels": (6, 7, 8), "name": "A"  }
    PA_MIDICAPTAIN_NANO_SWITCH_B = { "model": AdafruitSwitch(board.GP10), "pixels": (9, 10, 11), "name": "B"  }

    # PaintAudio MIDI Captain Mini (6 Switches)
    # Board Infos
    # Raspberry Pi Pico (RP2040)
    #
    # GP1  - FootSwitch 1
    # GP4  bat_chg_led
    # GP6  charging
    # GP7  NeoPixel
    # GP8  asyncio PWMOut frequency
    # GP9  - FootSwitch A
    # GP10 - FootSwitch B
    # GP11 - FootSwitch C
    # GP12 tft_dc   (SPI1 RX)
    # GP13 tft_cs   (Chip Select)
    # GP14 spi_clk  (SPI1SCK)
    # GP15 spi_mosi (SPI1 TX)
    # GP16 Midi GP16GP17 baudrate
    # GP17 Midi GP16GP17 baudrate
    # GP24 - FootSwitch 3
    # GP25 - FootSwitch 2
    PA_MIDICAPTAIN_MINI_SWITCH_1 = { "model": AdafruitSwitch(board.GP1),  "pixels": (0, 1, 2), "name": "1"  }
    PA_MIDICAPTAIN_MINI_SWITCH_2 = { "model": AdafruitSwitch(board.GP25), "pixels": (3, 4, 5), "name": "2"  }
    PA_MIDICAPTAIN_MINI_SWITCH_3 = { "model": AdafruitSwitch(board.GP24), "pixels": (6, 7, 8), "name": "3"  }
    PA_MIDICAPTAIN_MINI_SWITCH_A = { "model": AdafruitSwitch(board.GP9),  "pixels": (9, 10, 11), "name": "A"  }
    PA_MIDICAPTAIN_MINI_SWITCH_B = { "model": AdafruitSwitch(board.GP10), "pixels": (12, 13, 14), "name": "B"  }
    PA_MIDICAPTAIN_MINI_SWITCH_C = { "model": AdafruitSwitch(board.GP11), "pixels": (15, 16, 17), "name": "C"  }

    # PaintAudio MIDI Captain (10 Switches) EXPERIMENTAL/UNTESTED! 
    # Thanks to @Erikcb on the Kemper Forums!
    # Board Infos
    # Raspberry Pi Pico (RP2040)
    #
    # GP1  - FootSwitch 1
    # GP4  bat_chg_led
    # GP6  charging
    # GP7  NeoPixel
    # GP8  asyncio PWMOut frequency
    # GP9  - FootSwitch A
    # GP10 - FootSwitch B
    # GP11 - FootSwitch C
    # GP12 tft_dc   (SPI1 RX)
    # GP13 tft_cs   (Chip Select)
    # GP14 spi_clk  (SPI1SCK)
    # GP15 spi_mosi (SPI1 TX)
    # GP16 Midi GP16GP17 baudrate
    # GP17 Midi GP16GP17 baudrate
    # GP18 - Footswitch D
    # GP19 - Footswitch down
    # GP20 - FootSwitch up
    # GP23 - FootSwitch 4
    # GP24 - FootSwitch 3
    # GP25 - FootSwitch 2
    PA_MIDICAPTAIN_10_SWITCH_1    = { "model": AdafruitSwitch(board.GP1),  "pixels": (0, 1, 2), "name": "1"  }
    PA_MIDICAPTAIN_10_SWITCH_2    = { "model": AdafruitSwitch(board.GP25), "pixels": (3, 4, 5), "name": "2"  }
    PA_MIDICAPTAIN_10_SWITCH_3    = { "model": AdafruitSwitch(board.GP24), "pixels": (6, 7, 8), "name": "3"  }
    PA_MIDICAPTAIN_10_SWITCH_4    = { "model": AdafruitSwitch(board.GP23), "pixels": (9, 10, 11), "name": "4"  }
    PA_MIDICAPTAIN_10_SWITCH_UP   = { "model": AdafruitSwitch(board.GP20), "pixels": (12, 13, 14), "name": "Up"  }
    PA_MIDICAPTAIN_10_SWITCH_A    = { "model": AdafruitSwitch(board.GP9),  "pixels": (15, 16, 17), "name": "A"  }
    PA_MIDICAPTAIN_10_SWITCH_B    = { "model": AdafruitSwitch(board.GP10), "pixels": (18, 19, 20), "name": "B"  }
    PA_MIDICAPTAIN_10_SWITCH_C    = { "model": AdafruitSwitch(board.GP11), "pixels": (21, 22, 23), "name": "C"  }
    PA_MIDICAPTAIN_10_SWITCH_D    = { "model": AdafruitSwitch(board.GP18), "pixels": (24, 25, 26), "name": "D"  }
    PA_MIDICAPTAIN_10_SWITCH_DOWN = { "model": AdafruitSwitch(board.GP19), "pixels": (27, 28, 29), "name": "Dn"  }

###########################################################################################################################

    # USB Midi in/out for PA MIDICaptain devices. No UART, so ports have to be adafruit MIDI ports from 
    # the usb_midi module.
    @staticmethod
    def PA_MIDICAPTAIN_USB_MIDI(in_channel = None, out_channel = 0, in_buf_size = 2500):
        return AdfruitUsbMidiDevice(
            port_in = ports[0],
            port_out = ports[1],
            in_channel = in_channel,
            out_channel = out_channel,
            in_buf_size = in_buf_size
        )

    # DIN Midi in/out for PA MIDICaptain devices. Uses UART mode so the ports must be board GPIO pins.
    @staticmethod
    def PA_MIDICAPTAIN_DIN_MIDI(in_channel = None, out_channel = 0, in_buf_size = 2500):
        return AdfruitDinMidiDevice(
            gpio_in = board.GP16,
            gpio_out = board.GP17,
            in_channel = in_channel,
            out_channel = out_channel,
            baudrate = 31250,
            timeout = 0.001,
            in_buf_size = in_buf_size
        )

