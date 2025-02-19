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
     * Returns a list of all available actions.
     */
    async getAvailableActions(basePath = "") {
        if (this.#availableActions) return this.#availableActions;

        // This just loads the buffered version. To create the list, see the parser tests.
        this.#availableActions = JSON.parse(await Tools.fetch(basePath + "definitions/actions.json"));
        return this.#availableActions;
    }

    // /**
    //  * Generates the list of available actions using libCST and returns it (without setting 
    //  * the local buffer! this is mainly called by tests)
    //  */
    // async generateAvailableActions(basePath = "") {
    //     // Get TOC of clients
    //     const toc = JSON.parse(await Tools.fetch(basePath + "circuitpy/lib/pyswitch/clients/toc.php"));

    //     /**
    //      * Returns a direct child by name 
    //      */
    //     function getChild(node, name) {
    //         for(const child of node.children || []) {
    //             if (child.name == name) return child;
    //         }
    //         throw new Error("Child " + name + " not found");
    //     }

    //     // Get actions dir node
    //     const actions = getChild(getChild(toc, "kemper"), "actions");

    //     // Get python paths for all files (the files are already located in the Pyodide FS, so python 
    //     // can just open them to get their contents)
    //     const importPaths = [];

    //     function crawl(node, prefix = "pyswitch/clients/kemper/actions") {
    //         if (node.type == "file") {
    //             if (node.name.endsWith(".py") && !node.name.startsWith("__")) {
    //                 importPaths.push(prefix);
    //             }                
    //             return;
    //         }

    //         for (const child of node.children) {
    //             crawl(child, prefix + (prefix ? "/" : "") + child.name);
    //         }
    //     }
    //     crawl(actions);

    //     // Tell the python code which files to examine, process it and return the decoded result.
    //     const actionsJson = await this.runner.pyodide.runPython(`
    //         import json
    //         from parser.FunctionExtractor import FunctionExtractor
    //         pySwitchActions = FunctionExtractor(
    //             import_paths = json.loads('` + JSON.stringify(importPaths) + `')
    //         )
    //         json.dumps(pySwitchActions.get())
    //     `);

    //     return JSON.parse(actionsJson);
    // }
}