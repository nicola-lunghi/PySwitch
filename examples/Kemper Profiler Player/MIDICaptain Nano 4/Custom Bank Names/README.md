## Exampe Description

This shows how to use custom text output callbacks for the RIG_SELECT, RIG_AND_BANK_SELECT and BANK_UP/DOWN actions. The example has no practical use, this is just for demonstration! If they seem confusing at first, see this chart for what each action does:

|            | What it does?                                | What's displayed?                                           |
|------------|----------------------------------------------|-------------------------------------------------------------|
| Switch 1   | Select Rig 1 of current Bank                 | Target Rig with custom bank name, enlightened when selected |
| Switch 2   | Select Rig 2 in Bank 3                       | Target Rig with custom bank name, enlightened when selected |
| Switch A   | Toggle between Rigs 1 and 2 of current bank  | Current rig with custom bank name, always dimmed            |
| Switch B   | Next Bank (displaying the custom text)       | Target rig with custom bank name, always dimmed (*)         |

The bank names are overridden with custom names by using a custom callback function, see switches.py


(\*) For BANK_UP and BANK_DOWN, no state display is supported, so the lights are always dimmed. For the others, the full brightness is only used when the target rig is selected and display_mode is set to RIG_SELECT_DISPLAY_TARGET_RIG.

