## Exampe Description

**Switch 1:** Tuner Mode

**Switch 2:** Tap tempo

**Switch A:** FX Slot A

**Switch B:** Morph Button (\*)

(\*) The morph button is shown with a fixed color (Default: White, can be set using color parameter). However, you can set the color parameter to "kemper", which aligns the colors of switch B's label and LEDs according to the Morph Pedal position as reported by the Kemper. 

However, the Kemper has a bug here: The exposed state is just updated when you either change it via Expression pedal or in Rig Manager. The morph button does NOT update the value, meaning that the Kemper is in another morph state as it reports. 

To not report any falsy info (which i personally hate) this is deactivated by default. If you want to try it, just set color = "kemper" for the MORPH_BUTTON action:

```python
    # Switch B
    {
        "assignment": Hardware.PA_MIDICAPTAIN_NANO_SWITCH_B,
        "actions": [
            KemperActionDefinitions.MORPH_BUTTON(
                display = DISPLAY_FOOTER_2,
                color = "kemper"
            )
        ]
    }
```