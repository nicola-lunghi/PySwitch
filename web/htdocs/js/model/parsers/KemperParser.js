class KemperParser extends Parser {

    static DEVICE_TYPE_NANO_4 = 10;
    static DEVICE_TYPE_MINI_6 = 20;
    static DEVICE_TYPE_10 = 30;

    #py = null;
    #csts = null;

    /**
     * Creates the python libcst parser. Must be called at least once before 
     * the parser is actually used. Expects the PySwitchRunner.
     */
    async #init() {
        if (this.#py) return;        
        this.#py = await this.runner.pyodide.runPython(`            
            from PySwitchParser import PySwitchParser
            PySwitchParser()
        `);    
    }

    /**
     * Returns a CST (Concrete Syntax Tree) from the sources.
     */
    async parse() {
        if (this.#csts) return;
        await this.#init();

        const inputs_py = (await this.config.get()).inputs_py;
        const display_py = (await this.config.get()).display_py;

        this.#csts = {
            inputs_py: await this.#py.parse(inputs_py),
            display_py: await this.#py.parse(display_py)
        };
    }

    /**
     * Unparse a CST tree
     */
    async unparse() {
        if (!this.#csts) throw new Error("Please parse() before");
        await this.#init();

        return {
            inputs_py: await this.#py.unparse(this.#csts.inputs_py),
            display_py: await this.#py.unparse(this.#csts.display_py)
        }
    }

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Returns an array of all actions for the given input.
     * port must be an integer ID of the port (as defined in the board wrapper in python)
     */
    async getInputActions(port) {
        await this.parse();

        const json = this.#py.get_actions(await this.#getHardwareImportPath(), this.#csts.inputs_py, port);
        return JSON.parse(json);
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