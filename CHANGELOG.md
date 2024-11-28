# PySwitch v2.2.0
- Tempo-synced blinking switch LEDs (all examples using TAP_TEMPO now include this feature) or labels
- Show current bank colors for RIG_SELECT (...) and bank up/down action definitions
- RIG_SELECT (and the new RIG_AND_BANK_SELECT): 
    - Correct call sequence to also support the Kemper "Rig Btn Morph" option correctly. If you activate the option on the Kemper (System Menu), the actions will toggle morph state just like the internal Kemper switches.
    - Two display modes are supported:
        - Show the current rig and bank
        - Show the rig and bank which will be switched to when the switch is pushed.
    - Text of the display label can be set via a custom callback function.
    - Color of the display label can be set via a custom callback function.
- RIG_VOLUME_BOOST now remembers the current rig volume before turning the boost on, and restores this volume when disabled again.
- Added morph button support (sadly there is no feedback from kemper about the current state, so the action does not show any states)
- Fixed calibration of TunerDisplay (this now can also be customized in display.py as well as tuner colors and note names)
- Changes to configuration and general concept:
    - Conceptual changes:
        - Displays are not addressed via ID/index anymore, instead a reference to the DisplayLabel instances has to be passed to "display". See examples.
        - Conditions are replaced completely by callbacks, which provide more flexible programming of custom displays. See README.
        - ParameterAction and EffectEnableAction have been replaced completely with callbacks, too. See BinaryParameterCallback and EffectEnableCallback.
    - Minor changes to config:
        - communication.py: "valueProvider" no longer needed (now implemented in the mappings directly)
        - All members of KemperMappings now are functions (some still have been class attributes)

# PySwitch v2.1.2
- Memory usage optimized: 
    - Avoid keeping of config dictionaries for longer than __init__
    - Removed corner radius from display elements
    - "fake stroke" (DisplayLabel)
    - On-flash consts (micropython optimization)
    - Reduced class footprint
    -> Tested with big configuration (4 FX slot display labels, rig name, Tuner, 10 Switches with 3 LEDs each, Effect Enable Actions with expensive mappings on all switches) with no problems and still about 20% of RAM left
- Added examples
- Tuner sensitivity adjusted, colors changed for lighter ones

# PySwitch v2.1.1
- Added mappings for Effect Buttons I-IIII (set only, sadly there is no state feedback possibility from Kemper)

# PySwitch v2.1.0
- Bidirectional communication with the Kemper devices
- Tuner Splash showing tuner note and deviation from the note visually
- HoldAction to assign different actions on long press
- ParameterAction: Supports different comparison modes now
- Bug fixes / Unit Tests updated
 
# PySwitch v2.0.0
- Complete Rewrite (standalone firmware without dependency on PaintAudio Code, object oriented design etc.)
- Customization by config script
- Out-of-the-box Compatibility with PaintAudio MIDICaptain Nano (4 Switches) and Mini (6 Switches),
  configurable easily for other devices using the new Explore mode (Detect IO addressing for new devices)
- Activate auto-reload when switch 2 (GP25) is pressed during boot
- Conditions in switch assignents an display layouts, to make the configuration depending on device 
  parameters like the rig name
- ...

