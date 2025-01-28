class PySwitchRunner {

    #options = null;
    #runner = null;

    /**
     * Options:
     * {
     *     domNamespace: "pyswitch",      ID prefix for access to DOM elements from Python code
     *     updateIntervalMillis: 10,      Tick interval in milliseconds. On CircuitPython, the program does as much ticks as it can (in a while True loop),
     *                                    which in a browser woult block all user interaction, so the ticks are triggered in intervals.
     * }
     */
    constructor(options) {
        this.#options = options;        
    }

    /**
     * Set up Pyodide and copy all sources to the Emscripten virtual file system.
     */
    async init() {
        // Set up pyodide
        console.log("Initialize Pyodide");
        this.pyodide = await loadPyodide();
        
        // Load all files by GETing them and storing them to the virtual FS.
        // TODO this could be optimized
        console.log("Load files to python");

        await this.#loadModule("PySwitchRunner.py", "python/");
        await this.#loadModule("mocks.py", "python/");

        this.pyodide.FS.mkdir("wrappers");
        await this.#loadModule("wrappers/__init__.py", "python/");
        await this.#loadModule("wrappers/wrap_circuitpy.py", "python/");
        await this.#loadModule("wrappers/wrap_adafruit_midi.py", "python/");
        await this.#loadModule("wrappers/wrap_adafruit_led.py", "python/");
        await this.#loadModule("wrappers/wrap_adafruit_display.py", "python/");
        await this.#loadModule("wrappers/WrapDisplayDriver.py", "python/");
        
        //////////////////////////////////////////////////////////////////////////////////////////////

        this.pyodide.FS.mkdir("adafruit_midi");
        await this.#loadModule("adafruit_midi/__init__.py", "python/");
        await this.#loadModule("adafruit_midi/active_sensing.py", "python/");
        await this.#loadModule("adafruit_midi/channel_pressure.py", "python/");
        await this.#loadModule("adafruit_midi/control_change.py", "python/");
        await this.#loadModule("adafruit_midi/midi_continue.py", "python/");
        await this.#loadModule("adafruit_midi/midi_message.py", "python/");
        await this.#loadModule("adafruit_midi/mtc_quarter_frame.py", "python/");
        await this.#loadModule("adafruit_midi/note_off.py", "python/");
        await this.#loadModule("adafruit_midi/note_on.py", "python/");
        await this.#loadModule("adafruit_midi/pitch_bend.py", "python/");
        await this.#loadModule("adafruit_midi/polyphonic_key_pressure.py", "python/");
        await this.#loadModule("adafruit_midi/program_change.py", "python/");
        await this.#loadModule("adafruit_midi/start.py", "python/");
        await this.#loadModule("adafruit_midi/stop.py", "python/");
        await this.#loadModule("adafruit_midi/system_exclusive.py", "python/");
        await this.#loadModule("adafruit_midi/timing_clock.py", "python/");

        //////////////////////////////////////////////////////////////////////////////////////////////

        this.pyodide.FS.mkdir("pyswitch");
        await this.#loadModule("pyswitch/__init__.py");
        await this.#loadModule("pyswitch/misc.py");
        await this.#loadModule("pyswitch/stats.py");

        this.pyodide.FS.mkdir("pyswitch/clients");
        await this.#loadModule("pyswitch/clients/__init__.py");

        this.pyodide.FS.mkdir("pyswitch/clients/kemper");
        await this.#loadModule("pyswitch/clients/kemper/__init__.py");
        
        this.pyodide.FS.mkdir("pyswitch/clients/kemper/actions");            
        await this.#loadModule("pyswitch/clients/kemper/actions/__init__.py");
        await this.#loadModule("pyswitch/clients/kemper/actions/bank_select.py");
        await this.#loadModule("pyswitch/clients/kemper/actions/bank_up_down.py");
        await this.#loadModule("pyswitch/clients/kemper/actions/binary_switch.py");
        await this.#loadModule("pyswitch/clients/kemper/actions/effect_button.py");
        await this.#loadModule("pyswitch/clients/kemper/actions/effect_state.py");
        await this.#loadModule("pyswitch/clients/kemper/actions/looper.py");
        await this.#loadModule("pyswitch/clients/kemper/actions/morph.py");
        await this.#loadModule("pyswitch/clients/kemper/actions/rig_select_and_morph_state.py");
        await this.#loadModule("pyswitch/clients/kemper/actions/rig_select.py");
        await this.#loadModule("pyswitch/clients/kemper/actions/rig_up_down.py");
        await this.#loadModule("pyswitch/clients/kemper/actions/rig_volume_boost.py");
        await this.#loadModule("pyswitch/clients/kemper/actions/tempo.py");
        await this.#loadModule("pyswitch/clients/kemper/actions/tuner.py");

        this.pyodide.FS.mkdir("pyswitch/clients/kemper/mappings");  
        await this.#loadModule("pyswitch/clients/kemper/mappings/__init__.py");
        await this.#loadModule("pyswitch/clients/kemper/mappings/amp.py");
        await this.#loadModule("pyswitch/clients/kemper/mappings/bank.py");
        await this.#loadModule("pyswitch/clients/kemper/mappings/cabinet.py");
        await this.#loadModule("pyswitch/clients/kemper/mappings/effects.py");
        await this.#loadModule("pyswitch/clients/kemper/mappings/freeze.py");
        await this.#loadModule("pyswitch/clients/kemper/mappings/looper.py");
        await this.#loadModule("pyswitch/clients/kemper/mappings/morph.py");
        await this.#loadModule("pyswitch/clients/kemper/mappings/pedals.py");
        await this.#loadModule("pyswitch/clients/kemper/mappings/rig.py");
        await this.#loadModule("pyswitch/clients/kemper/mappings/rotary.py");
        await this.#loadModule("pyswitch/clients/kemper/mappings/select.py");
        await this.#loadModule("pyswitch/clients/kemper/mappings/tempo.py");
        
        this.pyodide.FS.mkdir("pyswitch/controller");  
        await this.#loadModule("pyswitch/controller/__init__.py");
        await this.#loadModule("pyswitch/controller/actions.py");
        await this.#loadModule("pyswitch/controller/AnalogAction.py");
        await this.#loadModule("pyswitch/controller/callbacks.py");
        await this.#loadModule("pyswitch/controller/Client.py");
        await this.#loadModule("pyswitch/controller/Controller.py");
        await this.#loadModule("pyswitch/controller/EncoderAction.py");
        await this.#loadModule("pyswitch/controller/ExploreModeController.py");
        await this.#loadModule("pyswitch/controller/InputControllers.py");
        await this.#loadModule("pyswitch/controller/MidiController.py");
        await this.#loadModule("pyswitch/controller/pager.py");
        await this.#loadModule("pyswitch/controller/RuntimeMeasurement.py");
        await this.#loadModule("pyswitch/controller/strobe.py");

        this.pyodide.FS.mkdir("pyswitch/hardware");  
        await this.#loadModule("pyswitch/hardware/__init__.py");

        this.pyodide.FS.mkdir("pyswitch/hardware/adafruit");  
        await this.#loadModule("pyswitch/hardware/adafruit/__init__.py");
        await this.#loadModule("pyswitch/hardware/adafruit/AdafruitDinMidiDevice.py");
        await this.#loadModule("pyswitch/hardware/adafruit/AdafruitEncoder.py");
        await this.#loadModule("pyswitch/hardware/adafruit/AdafruitPotentiometer.py");
        await this.#loadModule("pyswitch/hardware/adafruit/AdafruitSwitch.py");
        await this.#loadModule("pyswitch/hardware/adafruit/AdafruitUsbMidiDevice.py");

        this.pyodide.FS.mkdir("pyswitch/hardware/devices");  
        await this.#loadModule("pyswitch/hardware/devices/__init__.py");
        await this.#loadModule("pyswitch/hardware/devices/pa_midicaptain_10.py");
        await this.#loadModule("pyswitch/hardware/devices/pa_midicaptain_mini_6.py");
        await this.#loadModule("pyswitch/hardware/devices/pa_midicaptain_nano_4.py");
        await this.#loadModule("pyswitch/hardware/devices/pa_midicaptain.py");
        
        this.pyodide.FS.mkdir("pyswitch/ui");  
        await this.#loadModule("pyswitch/ui/__init__.py");
        await this.#loadModule("pyswitch/ui/elements.py");
        await this.#loadModule("pyswitch/ui/DisplaySplitContainer.py");
        await this.#loadModule("pyswitch/ui/layout.py");
        await this.#loadModule("pyswitch/ui/ui.py");
        await this.#loadModule("pyswitch/ui/UiController.py");
    }

    /**
     * Has to be called before running to provide a MIDI wrapper. This has to feature a send(bytes) method and
     * a messageQueue attribute holding incoming messages as raw bye arrays (one per queue entry).
     */
    setMidiWrapper(midiWrapper) {
        // Create access object
        if (!window.externalRefs) {
            window.externalRefs = {};
        }
        // If there is an old MIDI wrapper, detach it so it does not listen anymore
        if (window.externalRefs.midiWrapper) {
            window.externalRefs.midiWrapper.detach();
        }

        // Set the new MIDI wrapper. This will be accessed in the python MIDI wrappers.
        window.externalRefs.midiWrapper = midiWrapper;
    }

    /**
     * Returns if a MIDI wrapper is set
     */
    hasMidiWrapper() {
        if (!window.externalRefs) return false;
        return (!!window.externalRefs.midiWrapper);
    }

    /**
     * Run PySwitch, terminating an existing runner before.
     * The passed inputs and display must be python code for the inputs.py and display.py files.
     */
    async run(inputs_py, display_py) {
        console.log("Run PySwitch");
        // Set a dummy MIDI wrapper if none is there
        if (!this.hasMidiWrapper()) {
            this.setMidiWrapper(new DummyMidiWrapper());
        }

        // Stop if already running
        if (this.#runner) {
            this.#runner.stop()
        }        

        // Copy the configuration to the virtual FS
        this.pyodide.FS.writeFile("/home/pyodide/inputs.py", inputs_py);
        this.pyodide.FS.writeFile("/home/pyodide/display.py", display_py);

        // Run PySwitch!
        this.#runner = await this.pyodide.runPython(`
            from PySwitchRunner import PySwitchRunner
            runner = PySwitchRunner("` + this.#options.domNamespace + `", "` + this.#options.updateIntervalMillis + `")
            runner.init()
            runner      # Returns the runner as a JS proxy
        `);
    }

    /**
     * Load a file into the virtual Emscripten file system. fileName is the path and name of the file inside the virtual FS,
     * rscPath will be added as prefix if set for getting the files on the web server.
     */
    async #loadModule(fileName, srcPath) {
        const code = await (await fetch((srcPath ? srcPath : "") + fileName)).text();
        this.pyodide.FS.writeFile("/home/pyodide/" + fileName, code);
    }
}