## Example Description

|            | Action                            |
|------------|-----------------------------------|
| Switch 1   | Effect C                          |
| Switch 2   | Effect X                          |
| Switch 3   | Effect MOD                        |
| Switch 4   | Bank down                         |
| Switch Up  | Bank Up                           |
| Switch A   | Select Rig 1 of current bank (\*) |
| Switch B   | Select Rig 2 of current bank      |
| Switch C   | Select Rig 3 of current bank      |
| Switch D   | Select Rig 4 of current bank      |
| Switch Dn  | Select Rig 5 of current bank      |

*(\*) controls DISPLAY_FOOTER_2, see below*

The display uses some specials:
- The top two labels, and the left bottom one show effect states for the switches 1, 2 and 3, BUT with the names of some categories changed. A custom action and callback is used for this.
- The display on the bottom right shows the current bank and rig (connected to switch A, but could be any of the bottom ones), using a custom text formatting function to override the default behaviour.



