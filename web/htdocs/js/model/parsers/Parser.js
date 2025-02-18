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

    config = null;    // Configuration instance

    constructor(config, runner) {
        this.config = config;
        this.runner = runner;
    }

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Returns a device handler for the configuration
     */
    async device() {
        return Device.getInstance(this.config);
    }

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
}