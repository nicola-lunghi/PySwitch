# PySwitch v2.3.5
- Changed parameters for PagerAction (all config options now accessible as parameters directly). Examples have been adjusted.
- Added option to directly select pages (see proxy method of PagerAction, demonstrated in some new examples for the MIDI Captain 10)

### Emulator 2.3.5.5
- Auto-add quotes to page text fields
- Added color input help
- Added explanation to the client select dialog

### Emulator 2.3.5.4
- Added full support for all Paging functionality (see Pager and Select Page actions)
- Usability changes: 
    - Parameter comments now shown as tooltips to reduce information overflow
    - Better display names for some actions

# PySwitch v2.3.4
- Reset state of the Effect Button actions on rig changes
- RIG_SELECT_AND_MORPH_STATE now can be used inside [] brackets like any other action (action lists are flattened initially)
- Bug Fix in the Kemper Bidirectional Protocol Implementation: Send init beacon even if we already received keep-alive messages from a former connection. This makes re-connecting easier in development and the new Emulator currently being developed.
- Changed the order of the bottom LEDs, to be a mirror of the upper LEDs order. This makes way more sense for switches with two actions sharing the LEDs, where the second action used the wrong LED before. The fix was just swapping the pixel addressing in lib/pyswitch/hardware/devices, if you like the old order better, just copy the definitions into inputs.py (just the bottom switches) and swap them back to linear order.
- Finally there is a **Web-based Configuration Tool**, currently released in alpha phase: The **"PySwitch Emulator"!** See README. This can change patches with a graphical user interface, and directly load/save them to the device. Also, it can directly control your Kemper! PySwitch is running in an emulated Python environment called "Pyodide" to achieve that (the original PySwitch code, no fake!), which is very handy for configuring the controller, trying things out, even for development of new features!

### Emulator 2.3.4.3
- Updated Pyodide to 0.27.3, fixing issues on Safari on iOS


# PySwitch v2.3.3
- Fixed behaviour of bank preselect:
    - **BANK_SELECT**: Now also can override a previously made selection
    - **BANK_UP, BANK_DOWN**: Preselect mode added. Can be used to step through banks before selection.

# PySwitch v2.3.2
- Bug Fixes:
    - **RIG_SELECT_AND_MORPH_STATE, RIG_UP, RIG_DOWN, BANK_SELECT, BANK_UP, BANK_DOWN**:
        - Reset the internal morph state globally (like RIG_SELECT did before already)
    - **RIG_UP, RIG_DOWN**:
        - Fixed overflow behaviour (RIG_UP at rig "125-5" now switches to "1-1" and vice versa)
    - **BANK_SELECT** with Preselect Option enabled:
        - Do not enter preselect mode again when the bank is already selected        
    - **Tuner**:
        - All buttons disable the tuner now, also if no TUNER_MODE action is contained in the preset
        - Strobe: Only show one spot on all devices, and disable by default
    - The maximum number of banks was incorrectly set to 126 (now: 125)
    
- Added/extended Features:
    - Added an option "process_overridden_actions" to TunerDisplayCallback (disabled by default). If this is enabled, the buttons keep their functionality when in tuner mode. But still, all buttons trigger switching off the tuner.
    - **BANK_SELECT** with preselect option enabled: 
        - Will now also show the preselected bank in the rig name label
        - All RIG_SELECT switches will blink as well until the rig is selected


# PySwitch v2.3.1
- Bug fix crashing the controller in certain constellations


# PySwitch v2.3.0
- Added Expression Pedal support (for MIDI Captain 10-Switch versions). This includes renaming the switches.py file to inputs.py. See examples for the 10 switch MIDI Captain.
- Added support for the rotary wheel on the MIDI Captain 10-Switch versions. Both the rotary encoder as well as the push button can be mapped. See examples.
- Added BANK_SELECT action for changing/toggling banks but stay at the same rig
- Added RIG_UP and RIG_DOWN actions (see examples for the Nano 4)
- Added option to RIG_SELECT and RIG_AND_BANK_SELECT which remembers the current rig in "off" state and switches back to it when disabling again. 
- Added option to RIG_SELECT and etc. to regard the "Rig Btn Morph" setting in the Kemper when selecting the current rig again. See the CurryFlurry Example for the Mini 6.
See example Nano 4 -> tunetown Session.
- Tuner mode:
    - Disable tuner mode with any switch
    - Added strobe tuner using all available LEDs when in tuner mode (active by default, can be disabled with parameter "strobe" in TunerDisplayCallback / display.py if you do not like to use it)
- Morph Button: When pushing this, the displayed state will be toggled whatever the Kemper says. Only if the Kemper sends an updated value, it will be updated on the controller, too. Note: This does only work when morph is triggered from the Controller! When using the Kemper "Rig Btn Morph" option, this will not be reflected.
- Added Looper mappings (see example Nano 4 -> tunetown Session with Looper and Pages). 
- Added Paging: Use class PagerAction to step through multiple pages with individual actions. Also partial pages are possible. The actions are switched via callback, see example Nano 4 -> tunetown Session.with Looper and Pages.
- Tempo Display is now darker by default, and brightness for on and off states can be adjusted by using the "led_brightness_\*" parameters of the SHOW_TEMPO action
- Effect Button mappings now just toggle their states regardless of the state on the Kemper (much of you wanted this). Can be disabled to the old behaviour by setting use_internal_state to False.
- Default global brightness factors for LEDs and DisplayLabels can now be set optionally in config.py, see comments there.
- Now supporting file editing from the browser via MIDI using the <a href="https://github.com/Tunetown/MidiBridge">MidiBridge</a> library. <a href="https://demo.midibridge.tunetown.de">Click here</a> with your device connected to the computer via USB (no switches pressed!) and it will automatically connect. This needs no USB mounting/unmounting and is useful for quick experimenting and changing settings. Should also serve as proof-of-concept for building a visual editor in the future (!)
- The code from code.py now is moved to a function inside the init script of the module, so multi-boot scenarios (different firmwares on button presses on boot, like @gstrotmanns version does) are also possible. Unit tests added for the init script.
- Further performance optimizations, the following ones need config file adjustments:
    - Merged HoldAction into Footswitch controller (put "actionsHold" into the switch definition directly instead)
    - All Kemper action pre-definitions are now separated in files. In switches.py, you now have to omit the KemperActionDefinitions. prefixes, and import the action definitions you need separately (see examples) which is a huge memory benefit.
    Implementation Notes: kemper.py code is now way smaller and moved to pyswitch/clients/kemper/\__init__.py
    - Hardware implementations are now separated into files for the different MIDI Captains. At the top of inputs.py (formerly switches.py), adjust to the device you use, see examples.
    - Removed performance dot (remove this from display.py if exists)
    - Merged HierarchicalDisplayElement into DisplayElement (replace HierarchicalDisplayElement with DisplayElement in display.py)
    - Removed DisplaySplitContainer and subtractive layouting (manually set display areas instead in display.py, see examples)
    - Removed some redundant actions for the sake of memory savings:
        - RIG_AND_BANK_SELECT: Use RIG_SELECT instead (which now supports bank and bank_off parameters)
        - RIG_AND_BANK_SELECT_AND_MORPH_STATE: Use RIG_SELECT_AND_MORPH_STATE instead (which now supports bank and bank_off parameters)
        - MORPH_BUTTON_WITH_DISPLAY: Use MORPH_BUTTON instead, setting the color parameter to "kemper".
- Removed the davjunk example (the Arek77 example does the same but better), added several new examples

# PySwitch v2.2.2
- Morph pedal position can now be requested from the Kemper. The position can be visualized with colors (faded between red and blue). See tehguitarist's example. Thanks to @sumsar for the NRPN mapping info.
- Prepared support for transfering files from and to to device via MIDI SysEx. Currently no client for this is implemented yet, so this is deactivated by default. 

# PySwitch v2.2.1
- Added first experimental hardware assignments and example for MIDICaptain 10

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

