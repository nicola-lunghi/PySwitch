class KemperParser extends Parser {

    static DEVICE_TYPE_NANO_4 = 10;
    static DEVICE_TYPE_MINI_6 = 20;
    static DEVICE_TYPE_10 = 30;

    #py = null;
    #csts = null;

    // debug(debug) {
    //     this.#py.debug = true
    // }

    /**
     * Creates the python libcst parser. Must be called at least once before 
     * the parser is actually used. Expects the PySwitchRunner.
     */
    async #init() {
        if (this.#py) return;        
        this.#py = await this.runner.pyodide.runPython(`            
            from parser.PySwitchParser import PySwitchParser
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
     * Returns an instance of Input.py
     * port must be an integer ID of the port (as defined in the board wrapper in python)
     */
    async input(port) {
        await this.parse();

        return this.#py.input(
            this.#csts.inputs_py,
            await this.#getHardwareImportPath(), 
            port
        );
    }

    /**
     * Replaces the passed input in the current CST.
     */
    async replaceInput(input) {
        await this.parse();
        
        this.#csts.inputs_py = this.#py.replace_input(
            this.#csts.inputs_py,
            input
        );
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