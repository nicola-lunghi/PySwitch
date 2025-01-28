class PySwitch {

    ui = null;                  // User Interface implementation
    pyswitch = null;            // PySwitch runner
    
    bridge = null;              // MIDI bridge handler (connects to the Controller running PyMidiBridge)
    //client = null;              // MIDI client device handler (connects to the Kemper)
    
    constructor(options) {
        this.pyswitch = new PySwitchRunner(options);        
    }

    async run() {
        // Set up MIDI bridge (this sets up Web MIDI which we can reuse)
        this.bridge = new MidiBridgeHandler();
        await this.bridge.init();
        
        // Initialize UI (settings panel etc.)
        this.ui = new PySwitchUI(this);
        await this.ui.init();

        // Initialize PySwitch (this starts Pyodide and copies all necessary sources to the Emscripten virtual file system)
        await this.pyswitch.init();

        // TMP get demo config
        const inputs_py = await (await fetch("python/inputs.py")).text();
        const display_py = await (await fetch("python/display.py")).text();

        // Run PySwitch
        await this.pyswitch.run(inputs_py, display_py);
    }
}