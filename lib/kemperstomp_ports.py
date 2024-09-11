#################################################################################################################################
# 
# Ports configuration for kemperstomp. This helps addressing the different devices. Only change this when either
# one of the supported devices has been updated or new devices are added.
#
#################################################################################################################################
 
import board

class Ports:
    # PaintAudio MIDI Captain Nano (4 Switches)
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
    PA_MIDICAPTAIN_NANO_SWITCH_1 = { "port": board.GP1,  "pixels": (0, 1, 2) }
    PA_MIDICAPTAIN_NANO_SWITCH_2 = { "port": board.GP25, "pixels": (3, 4, 5) }
    PA_MIDICAPTAIN_NANO_SWITCH_3 = { "port": board.GP9,  "pixels": (6, 7, 8) }
    PA_MIDICAPTAIN_NANO_SWITCH_4 = { "port": board.GP10, "pixels": (9, 10, 11) }

    # PaintAudio MIDI Captain Mini (6 Switches)
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
    # GP9  - FootSwitch 4
    # GP10 - FootSwitch 5
    # GP11 - FootSwitch 6
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
    # GP24 - FootSwitch 3
    # GP25 - FootSwitch 2
    # GP26
    # GP27
    # GP28
    PA_MIDICAPTAIN_MINI_SWITCH_1 = { "port": board.GP1,  "pixels": (0, 1, 2) }
    PA_MIDICAPTAIN_MINI_SWITCH_2 = { "port": board.GP25, "pixels": (3, 4, 5) }
    PA_MIDICAPTAIN_MINI_SWITCH_3 = { "port": board.GP24, "pixels": (6, 7, 8) }
    PA_MIDICAPTAIN_MINI_SWITCH_4 = { "port": board.GP9,  "pixels": (9, 10, 11) }
    PA_MIDICAPTAIN_MINI_SWITCH_5 = { "port": board.GP10, "pixels": (12, 13, 14) }
    PA_MIDICAPTAIN_MINI_SWITCH_6 = { "port": board.GP11, "pixels": (15, 16, 17) }
