## Exampe Description

This selects rigs 1 to 4 with all four switches of the Nano. Holding A or B additionally changes the bank (up or down)

The next bank selected on long press of A and B is also displayed using one LED on each switch. 

**Note that the controller does not know (yet) about an eventual restriction of max. bank (Kemper setting "Max. Banks"), so the shown color does not regard that setting!**

**NEW as of v2.2.2:** Morph state is visualized using one of the LEDs for RIG_SELECT actions, when the rig is selected (this can be changed using the parameter "morph_only_when_enabled").

LED Usage is as follows:

|                 | LED1                                         | LED2                                         | LED3
|-----------------|----------------------------------------------|----------------------------------------------|----------------------------------------------------|
| Switches 1 & 2  | Bank color, highlighted when rig is selected | Bank color, highlighted when rig is selected | Morph state when rig is selected, else: Bank color |
| Switches A & B  | Bank color, highlighted when rig is selected | Target bank color for bank up/dn (\*)        | Morph state when rig is selected, else: Bank color |

*(\*) This can be disabled by setting the use_leds option on the BANK_UP and BANK_DOWN actions to False, so the main action will take up the LED.*