class PySwitchRunner {

    #options = null;

    constructor(options) {
        this.#options = options;        
    }

    async init() {
        this.pyodide = await loadPyodide();
        
        await this.#loadModule("PyRunner.py", "python/");
        await this.#loadModule("inputs.py", "python/");
        await this.#loadModule("display.py", "python/");

        this.pyodide.FS.mkdir("mocks");
        await this.#loadModule("mocks/__init__.py", "python/");
        await this.#loadModule("mocks/mocks_lib.py", "python/");
        await this.#loadModule("mocks/mocks_circuitpy.py", "python/");
        await this.#loadModule("mocks/mocks_adafruit_midi.py", "python/");
        await this.#loadModule("mocks/mocks_adafruit_led.py", "python/");
        await this.#loadModule("mocks/mocks_adafruit_display.py", "python/");

        this.pyodide.FS.mkdir("mocks/display");
        await this.#loadModule("mocks/display/__init__.py", "python/");
        await this.#loadModule("mocks/display/WebDisplayDriver.py", "python/");

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

    async run(midiWrapper) {
        window.midiWrapper = midiWrapper;
        
        await this.pyodide.runPython(`
            from PyRunner import PyRunner
            runner = PyRunner("` + this.#options.domNamespace + `", "` + this.#options.updateIntervalMillis + `")
            runner.init()            
        `);

        midiWrapper.onmidimessage = async function(event) {
            // Check if its a sysex message
            if (event.data[0] != 0xf0 || event.data[event.data.length - 1] != 0xf7) {
                return;
            }

            const manufacturerId = Array.from(event.data).slice(1, 4);
            const data = Array.from(event.data).slice(4, event.data.length - 1);
            
            // Pass it to the bridge
            await bridge.receive({
                manufacturerId: manufacturerId,
                data: data
            });
        }
    }

    async #loadModule(fileName, srcPath) {
        const code = await (await fetch((srcPath ? srcPath : "") + fileName)).text();
        this.pyodide.FS.writeFile("/home/pyodide/" + fileName, code);
    }
}