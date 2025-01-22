## Example Description

This demonstrated how expression pedals can be added to the inputs list to control stuff.

**Pedal 1:** Rig Volume
**Pedal 2:** Morph State

The pedals per default use auto-calibration similar to the way the Kemper does. The pedal range is calibrated all the time, just rock the pedal up and down once to get the full range, reboot the controller to reset calibration.

If you like to switch off auto-calibration, set the parameter "auto_calibrate" of ContinuousAction to False (see inputs.py).
 

|            | Action: Short press          | Action: Long Press       |
|------------|------------------------------|--------------------------|
| Switch 1   | Effect A                     |                          |
| Switch 2   | Effect B                     |                          |
| Switch 3   | Effect C                     |                          |
| Switch 4   | Effect D                     | Tuner Mode               |
| Switch Up  | Effect X                     | Bank Up                  |
| Switch A   | Select Rig 1 of current bank |                          |
| Switch B   | Select Rig 2 of current bank |                          |
| Switch C   | Select Rig 3 of current bank |                          |
| Switch D   | Select Rig 4 of current bank |                          |
| Switch Dn  | Select Rig 5 of current bank | Bank down                |


