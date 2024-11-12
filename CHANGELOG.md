# 2.1.2
- Memory usage optimized: 
    - Avoid keeping of config dictionaries for longer than __init__
    - Removed corner radius from display elements
    - "fake stroke" (DisplayLabel)
    - On-flash consts (micropython optimization)
    - Reduced class footprint
    -> Tested with big configuration (4 FX slot display labels, rig name, Tuner, 10 Switches with 3 LEDs each, Effect Enable Actions with expensive mappings on all switches) with no problems and still about 20% of RAM left
- Added examples
- Tuner sensitivity adjusted, colors changed for lighter ones

# 2.1.1
- Added mappings for Effect Buttons I-IIII (set only, sadly there is no state feedback possibility from Kemper)

# 2.1.0
- Bidirectional communication with the Kemper devices
- Tuner Splash showing tuner note and deviation from the note visually
- HoldAction to assign different actions on long press
- ParameterAction: Supports different comparison modes now
- Bug fixes / Unit Tests updated
 
# 2.0.0
- Complete Rewrite (standalone firmware without dependency on PaintAudio Code, object oriented design etc.)
- Customization by config script
- Out-of-the-box Compatibility with PaintAudio MIDICaptain Nano (4 Switches) and Mini (6 Switches),
  configurable easily for other devices using the new Explore mode (Detect IO addressing for new devices)
- Activate auto-reload when switch 2 (GP25) is pressed during boot
- Conditions in switch assignents an display layouts, to make the configuration depending on device 
  parameters like the rig name
- ...

