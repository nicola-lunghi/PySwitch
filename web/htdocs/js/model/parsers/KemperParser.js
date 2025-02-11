class KemperParser extends Parser {

    static DEVICE_TYPE_NANO_4 = 10;
    static DEVICE_TYPE_MINI_6 = 20;
    static DEVICE_TYPE_10 = 30;

    #parser = null;
    #cst = null;
    
    /**
     * Creates the python libcst parser. Must be called at least once before 
     * the parser is actually used. Expects the PySwitchRunner.
     */
    async init() {
        if (this.#parser) return;        
        this.#parser = await this.runner.pyodide.runPython(`            
            from PySwitchParser import PySwitchParser
            PySwitchParser()
        `);    
    }

    /**
     * Returns a CST (Concrete Syntax Tree) from the sources.
     */
    async parse() {
        if (this.#cst) return this.#cst;
        if (!this.#parser) throw new Error("Please call init() before");

        const inputs_py = (await this.config.get()).inputs_py;
        const display_py = (await this.config.get()).display_py;

        this.#cst = {
            inputs_py: await this.#parser.parse(inputs_py),
            display_py: await this.#parser.parse(display_py)
        };

        return this.#cst;        
    }

    /**
     * Unparse a CST tree
     */
    async unparse() {
        if (!this.#parser) throw new Error("Please call init() before");
        if (!this.#cst) throw new Error("Please parse() before");

        return {
            inputs_py: await this.#parser.unparse(this.#cst.inputs_py),
            display_py: await this.#parser.unparse(this.#cst.display_py)
        }
    }

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Returns an array containing all inputs, represented by KemperParserInput instances, which
     * are possible on the device the config targets on.
     */
    async inputs() {
        const hardwareHandler = new KemperHardware(this);
        return hardwareHandler.get();
    }

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////

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