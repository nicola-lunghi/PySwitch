class PySwitch {

    ui = null;                  // User Interface implementation
    pyswitch = null;            // PySwitch runner
    
    #midiAccess = null;          // MIDIAccess instance
    
    constructor(options) {
        this.pyswitch = new PySwitchRunner(options);
        this.ui = new PySwitchUI(this);
    }

    async run() {
        // Set up Web MIDI
        await this.#initMidi();

        // Initialize UI (settings panel etc.)
        await this.ui.init();

        // Initialize PySwitch (this starts Pyodide and copies all necessary sources to the Emscripten virtual file system)
        await this.pyswitch.init();

        // TMP get demo config
        const inputs_py = await (await fetch("python/inputs.py")).text();
        const display_py = await (await fetch("python/display.py")).text();

        // Run PySwitch
        await this.pyswitch.run(inputs_py, display_py);
    }
  
    /**
     * Sets up Web MIDI communication
     */
    async #initMidi() {
        const that = this

        return new Promise(function(resolve, reject) {
            async function onMIDISuccess(midiAccess) {
                if (!midiAccess.sysexEnabled) {
                    reject({ message: "You must allow SystemExclusive messages" });
                }

                // Use a handler class for accessing the bridge and creating the connection
                that.#midiAccess = midiAccess;

                resolve();
            }

            async function onMIDIFailure(msg) {
                reject({ message: "Failed to get MIDI access: " + msg });
            }

            navigator.requestMIDIAccess({ sysex: true })
                .then(onMIDISuccess, onMIDIFailure);
        });
    }

    /**
     * Gets a port list, which is an array of objects like:
     * {
     *     input:
     *     output:
     * }
     */
    getMatchingPortPairs() {
        const ret = [];

        // Inputs
        for (const input of this.#midiAccess.inputs) {
            const in_handler = input[1];

            // Get corresponding output
            for (const output of this.#midiAccess.outputs) {
                const out_handler = output[1];

                if ((out_handler.manufacturer == in_handler.manufacturer) && (out_handler.name == in_handler.name)) {
                    ret.push({
                        name: out_handler.name,
                        input: in_handler,
                        output: out_handler
                    });
                }
            }
        }

        return ret;
    } 
}