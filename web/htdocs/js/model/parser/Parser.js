/**
 * Parser base class. Implements the basic parsing (using python helpers a lot), while the
 * child class(es) add client specific information.
 */
class Parser {

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////

    #pySwitchParser = null;

    #availableActions = null;
    #availableMappings = null;

    config = null;    // Configuration instance
    basePath = null;

    constructor(config, runner, basePath = "") {
        this.config = config;
        this.runner = runner;
        this.basePath = basePath;
    }

    /**
     * Creates the python libcst parser. Must be called at least once before 
     * the parser is actually used. Expects the PySwitchRunner.
     */
    async #init() {
        if (this.#pySwitchParser) return;
        
        const device = await this.device();
        const clients = (await Client.getAvailable(this.basePath)).map((item) => item.id);

        this.#pySwitchParser = await this.runner.pyodide.runPython(`         
            from parser.PySwitchParser import PySwitchParser
            PySwitchParser(
                hw_import_path         = "` + device.getHardwareImportPath() + `",
                available_clients_json = '` + JSON.stringify(clients) + `',
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
    updateConfig() {
        const src = this.#pySwitchParser.to_source().toJs();
        
        this.config.set({
            inputs_py: src.get("inputs_py"),
            display_py: src.get("display_py")
        });
    }

    /**
     * Update the config with new code for a single file and reset the parser
     */
    async updateFromSource(fileName, code) {
        const data = await this.config.get();
        data[fileName] = code;
        await this.updateFromData(data);
    }

    /**
     * Update the config with new code for all files and reset the parser
     */
    async updateFromData(data) {
        this.config.set(data);
        await this.#pySwitchParser.from_source(data.inputs_py, data.display_py);
    }    

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Returns a device handler for the configuration (a config can only have one device)
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

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Returns all available display labels
     */
    async getAvailableDisplays() {
        const displays = JSON.parse(this.#pySwitchParser.displays());

        return displays.filter((item) => item != "Splashes");
    }

    /**
     * Returns a list of all available actions, with mixed in meta information
     */
    async getAvailableActions() {
        if (this.#availableActions) return this.#availableActions;

        // This just loads the buffered version. To create the list, see the parser tests.
        this.#availableActions = JSON.parse(await Tools.fetch(this.basePath + "definitions/actions.json"));
        
        // Put in meta info where exists
        for (const client of this.#availableActions) {
            await this.#mixInMetaInformation(client.actions, ClientFactory.getInstance(client.client));
        }
        
        return this.#availableActions;
    }

    /**
     * Returns an actions definition or null if not found
     */
    async getActionDefinition(name, clientId) {
        const clients = await this.getAvailableActions();

        for (const client of clients) {
            if (!client.id == clientId) continue;

            for (const action of client.actions) {
                if (action.name == name) {
                    return action
                }
            }    
        }
        return null;
    }

    /**
     * Returns a list of all available actions, with mixed in meta information
     */
    async getAvailableMappings() {
        if (this.#availableMappings) return this.#availableMappings;

        // This just loads the buffered version. To create the list, see the parser tests.
        this.#availableMappings = JSON.parse(await Tools.fetch(this.basePath + "definitions/mappings.json"));

        // Put in meta info where exists
        for (const client of this.#availableMappings) {
            await this.#mixInMetaInformation(client.mappings, ClientFactory.getInstance(client.client));
        }

        return this.#availableMappings;
    }

    /**
     * For a list of function descriptors, this adds meta descriptor information (unbuffered)
     */
    async #mixInMetaInformation(functions, client) {
        const that = this;
        const meta = JSON.parse(await Tools.fetch(this.basePath + "definitions/meta.json"));

        /**
         * Searches a function meta definition for the given function name.
         * No default resolving here.
         */
        function searchFunctionDefinition(funcName) {
            for (const clientDef of meta) {
                if (clientDef.client != client.id) continue;

                for (const definition of clientDef.entities) {
                    if (definition.entityName == funcName) {
                        return definition;
                    }
                }    
            }
            return null;
        }

        /**
         * Searches a parameter meta definition for the given function name and parameter name. 
         * No default resolving here.
         */
        function searchParameterDefinition(funcName, paramName) {
            const definition = searchFunctionDefinition(funcName);
            if (!definition) return null;

            for (const param of definition.parameters) {
                if (param.name == paramName) {                            
                    return param;
                }
            }                    

            return null;
        }

        /**
         * Returns function metadata
         */
        async function getFunctionMeta(func) {
            // Search for specific definition first
            let def = searchFunctionDefinition(func.name);

            // Strip parameters (waste of memory)
            if (def) {
                def = structuredClone(def);
                delete def.entityName;    
                delete def.parameters; 
                delete def.comment;    
            }

            return client.createFunctionMeta(that, def, func);
        }

        /**
         * Tries to find meta info for a parameter, resolving to default if not found
         */
        async function getParameterMeta(func, param) {
            // Search for specific definition first
            let def = searchParameterDefinition(func.name, param.name);

            if (!def) {
                // Search for default
                def = searchParameterDefinition("default", param.name);
            }

            return client.createParameterMeta(that, def, param);
        }

        // Scan function definitions
        for (const func of functions) {
            for (const param of func.parameters) {
                param.meta = await getParameterMeta(func, param);
            }

            func.meta = await getFunctionMeta(func);
        }
    }
}