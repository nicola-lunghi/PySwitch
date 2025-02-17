class KemperParser extends Parser {

    static DEVICE_TYPE_NANO_4 = 10;
    static DEVICE_TYPE_MINI_6 = 20;
    static DEVICE_TYPE_10 = 30;

    #pySwitchParser = null;

    /**
     * Creates the python libcst parser. Must be called at least once before 
     * the parser is actually used. Expects the PySwitchRunner.
     */
    async #init() {
        if (this.#pySwitchParser) return;
        
        this.#pySwitchParser = await this.runner.pyodide.runPython(`         
            from parser.PySwitchParser import PySwitchParser
            PySwitchParser(
                hw_import_path = "` + (await this.#getHardwareImportPath()) + `"
            )
        `);

        const inputs_py = (await this.config.get()).inputs_py;
        const display_py = (await this.config.get()).display_py;

        await this.#pySwitchParser.from_source(inputs_py, display_py);
    }

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Returns an instance of Input.py, which handles all operations on the input.
     * port must be an integer ID of the port (as defined in the board wrapper in python)
     */
    async input(port) {
        await this.#init();
        return this.#pySwitchParser.input(port);
    }

    /**
     * Returns a (proxied) Map holding the sources of the current parser state.
     */
    async source() {
        await this.#init();
        return this.#pySwitchParser.to_source();
    }

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Returns the hardware definition script file name in the lib/pyswitch/hardware/devices/ folder
     */
    async #getHardwareImportPath() {
        switch (await this.getDeviceType()) {
            case KemperParser.DEVICE_TYPE_NANO_4:
                return "pyswitch.hardware.devices.pa_midicaptain_nano_4"

            case KemperParser.DEVICE_TYPE_MINI_6:
                return "pyswitch.hardware.devices.pa_midicaptain_mini_6"

            case KemperParser.DEVICE_TYPE_10:
                return "pyswitch.hardware.devices.pa_midicaptain_10"
        }
    }

    /**
     * Returns the class(es) to set on the device element
     */
    async getDeviceClass() {
        switch (await this.getDeviceType()) {
            case KemperParser.DEVICE_TYPE_NANO_4:
                return "midicaptain midicaptain-nano-4";

            case KemperParser.DEVICE_TYPE_MINI_6:
                return "midicaptain midicaptain-mini-6";

            case KemperParser.DEVICE_TYPE_10:
                return "midicaptain midicaptain-10";
        }
    }
    
    /**
     * Returns the device type
     */
    async getDeviceType() {
        const data = await this.config.get();

        if (data.inputs_py.includes("pyswitch.hardware.devices.pa_midicaptain_nano_4")) {
            return KemperParser.DEVICE_TYPE_NANO_4;
        }
        if (data.inputs_py.includes("pyswitch.hardware.devices.pa_midicaptain_mini_6")) {
            return KemperParser.DEVICE_TYPE_MINI_6;
        }
        if (data.inputs_py.includes("pyswitch.hardware.devices.pa_midicaptain_10")) {
            return KemperParser.DEVICE_TYPE_10;
        }
        
        throw new Error("Unknown device type");
    }

    /**
     * Returns a ClientDetector instance for the configuration
     */
    async getClientDetector() {
        const data = await this.config.get();
        
        if (data.inputs_py.includes("pyswitch.clients.kemper")) {
            return new KemperDetector();
        }

        throw new Error("Unknown client type");
    }

    /**
     * Must return a virtual client
     */
    async getVirtualClient(config = {}) {
        return new VirtualKemperClient(
            {
                ...{
                    productType: 2,               // KPP
                    simulateMorphBug: true        // Simulate the morph button bug
                },
                ...config
            }
        );
    }
}