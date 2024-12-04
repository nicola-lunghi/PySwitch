## Exampe Description

Switch 1: Tuner Mode
Switch 2: Tap tempo
Switch A: FX Slot A
Switch B: Morph Button 

The morph button is shown with a fixed color (can be set using color parameter) here. There is an alternative version MORPH_BUTTON_WITH_DISPLAY, which aligns the colors of switch B's label and LEDs according to the Morpg Pedal position as reported by the Kemper. However, the Kemper has a bug here: The exposed state is just updated when you either change it via Expression pedal or in Rig Manager. The morph button does NOT update the value, meaning that the Kemper is in another morph state as it reports. 

To not report any falsy info (which i personally hate) this is not used here in the example. If you want to try this, just change MORPH_BUTTON action for MORPH_BUTTON_WITH_DISPLAY.