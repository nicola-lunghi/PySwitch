class KemperParser extends Parser {

    #parser = null;
    
    /**
     * Creates the python libcst parser. Must be called at least once before 
     * the parser is actually used. Expects the PySwitchRunner.
     */
    async init(runner) {
        if (this.parser) return;        
        this.#parser = await runner.pyodide.runPython(`            
            from PySwitchParser import PySwitchParser
            PySwitchParser()
        `);    
    }

    /**
     * Returns a CST (Concrete Syntax Tree) from the sources.
     */
    async parse() {
        if (!this.#parser) throw new Error("Please call init() before");

        const inputs_py = (await this.config.get()).inputs_py;
        const display_py = (await this.config.get()).display_py;

        return {
            inputs_py: await this.#parser.parse(inputs_py),
            display_py: await this.#parser.parse(display_py)
        }
    }

    /**
     * Unparse a CST tree
     */
    async unparse(cst) {
        if (!this.#parser) throw new Error("Please call init() before");

        return {
            inputs_py: await this.#parser.unparse(cst.inputs_py),
            display_py: await this.#parser.unparse(cst.display_py)
        }
    }

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Returns the class(es) to set on the device element
     */
    async getClass() {
        const data = await this.config.get();

        if (data.inputs_py.includes("pyswitch.hardware.devices.pa_midicaptain_nano_4")) {
            return "midicaptain midicaptain-nano-4";
        }
        if (data.inputs_py.includes("pyswitch.hardware.devices.pa_midicaptain_mini_6")) {
            return "midicaptain midicaptain-mini-6";
        }
        if (data.inputs_py.includes("pyswitch.hardware.devices.pa_midicaptain_10")) {
            return "midicaptain midicaptain-10";
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