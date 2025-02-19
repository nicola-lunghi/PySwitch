class Parser {

    static async getInstance(config, runner) {
        const data = await config.get();

        if (data.inputs_py.includes("pyswitch.clients.kemper")) {
            return new KemperParser(config, runner);
        }

        console.warn("Unknown client type, defaulting to Kemper");
        return new KemperParser(config, runner);
    }

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////

    #pySwitchParser = null;

    #availableActions = null;
    #availableMappings = null;

    config = null;    // Configuration instance

    constructor(config, runner) {
        this.config = config;
        this.runner = runner;
    }

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Must return a ClientDetector instance for the configuration
     */
    async getClientDetector() {
        throw new Error("Must be implemented in child classes");
    }

    /**
     * Can return a virtual client, or null if the parsers config does not support a virtual client.
     * config is an options object for the virtual client.
     */
    async getVirtualClient(config = {}) {
        return null;
    }    

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Creates the python libcst parser. Must be called at least once before 
     * the parser is actually used. Expects the PySwitchRunner.
     */
    async #init() {
        if (this.#pySwitchParser) return;
        
        const device = await this.device();

        this.#pySwitchParser = await this.runner.pyodide.runPython(`         
            from parser.PySwitchParser import PySwitchParser
            PySwitchParser(
                hw_import_path = "` + device.getHardwareImportPath() + `"
            )
        `);

        this.#pySwitchParser.init(this);

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
     * Updates the underlying config from the current CSTs. Called by python code after updates to the trees.
     */
    update_config() {
        const src = this.#pySwitchParser.to_source().toJs();

        this.config.set({
            inputs_py: src.get("inputs_py"),
            display_py: src.get("display_py")
        });
    }

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Returns a device handler for the configuration
     */
    async device() {
        return Device.getInstance(this.config);
    }

    /**
     * Returns hardware info (available inputs) for the given config
     */
    async getHardwareInfo() {
        const device = await this.device();
        
        const hardwareJson = await this.runner.pyodide.runPython(`
            import json
            from parser.PySwitchHardware import PySwitchHardware
            pySwitchHardware = PySwitchHardware()
            json.dumps(pySwitchHardware.get("` + device.getHardwareImportPath() + `"))
        `);

        return JSON.parse(hardwareJson);
    }

    /**
     * Returns a list of all available actions, with mixed in meta information
     */
    async getAvailableActions(basePath = "") {
        if (this.#availableActions) return this.#availableActions;

        // This just loads the buffered version. To create the list, see the parser tests.
        this.#availableActions = JSON.parse(await Tools.fetch(basePath + "definitions/actions.json"));
        
        // Put in meta info where exists
        await this.#mixInMetaInformation(basePath, this.#availableActions);
        
        return this.#availableActions;
    }

    /**
     * Returns a list of all available actions, with mixed in meta information
     */
    async getAvailableMappings(basePath = "") {
        if (this.#availableMappings) return this.#availableMappings;

        // This just loads the buffered version. To create the list, see the parser tests.
        this.#availableMappings = JSON.parse(await Tools.fetch(basePath + "definitions/mappings.json"));

        // Put in meta info where exists
        await this.#mixInMetaInformation(basePath, this.#availableMappings);

        return this.#availableMappings;
    }

    /**
     * For a list of function descriptors, this adds meta descriptor information (unbuffered)
     */
    async #mixInMetaInformation(basePath, functions) {
        const meta = JSON.parse(await Tools.fetch(basePath + "definitions/meta.json"));

        /**
         * Searches a parameter meta definition for the given function name and parameter name. 
         * No default resolving here.
         */
        function searchParameterDefinition(funcName, paramName) {
            for (const definition of meta.parameters) {
                if (definition.entityName == funcName) {
                    for (const param of definition.parameters) {
                        if (param.name == paramName) {
                            
                            return param;
                        }
                    }                    
                }
            }
            return null;
        }

        /**
         * Tries to find meta info for a parameter, resolving to default if not found
         */
        function getParameterMeta(func, param) {
            // Search for specific definition first
            let def = searchParameterDefinition(func.name, param.name);

            if (!def) {
                // Search for default
                def = searchParameterDefinition("default", param.name);
            }

            return def;
        }

        // Scan function definitions
        for (const func of functions) {
            for (const param of func.parameters) {
                // See if we have any meta information for the parameter
                const pmeta = getParameterMeta(func, param);
                if (!pmeta) continue;

                param.meta = pmeta;
            }
        }
    }
}