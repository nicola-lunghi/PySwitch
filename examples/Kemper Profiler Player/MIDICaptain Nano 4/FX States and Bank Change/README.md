## Exampe Description

This example is like the FX State example, but adds bank up/down functionality to the switches 1 and 2 on long pressing.

|            | Action: Short Press          | Action: Long Press       |
|------------|------------------------------|--------------------------|
| Switch 1   | Effect A                     | Bank Down                |
| Switch 2   | Effect B                     | Bank Up                  |
| Switch A   | Effect DLY                   |                          |
| Switch B   | Effect REV                   |                          |


If you do not want to have a LED segment assigned to the hold action (or any other), just add the "use_leds = False" option (see definitions of the actions).

