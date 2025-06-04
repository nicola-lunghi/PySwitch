## Exampe Description

This example is like the FX State example, but adds bank up/down functionality to the switches 1 and 2 on long pressing.

Additionally, this uses the extended version of EFFECT_STATE called EFFECT_STATE_EXT, which shows distinct names for each effect type. This takes a bit more memory, but in case of the 4/6 switch devices, this is no concern normally.

|            | Action: Short Press          | Action: Long Press       |
|------------|------------------------------|--------------------------|
| Switch 1   | Effect A                     | Bank Down                |
| Switch 2   | Effect B                     | Bank Up                  |
| Switch A   | Effect DLY                   |                          |
| Switch B   | Effect REV                   |                          |


If you do not want to have a LED segment assigned to the hold action (or any other), just add the "use_leds = False" option (see definitions of the actions).

