class Parser {

    static getInstance(config, runner) {
        return new KemperParser(config, runner);
    }

    /////////////////////////////////////////////////////////////

    config = null;    // Configuration instance

    constructor(config, runner) {
        this.config = config;
        this.runner = runner;
    }

    /**
     * Returns a CST (Concrete Syntax Tree) from the sources.
     * Expects the PySwitchRunner.
     */
    async parse() {
        throw new Error("Must be implemented in child classes");
    }

    /**
     * Returns the CSS class(es) to set on the device element
     */
    async getClass() {
        throw new Error("Must be implemented in child classes");
    }

    /**
     * Returns a ClientDetector instance for the configuration
     */
    async getClientDetector() {
        throw new Error("Must be implemented in child classes");
    }

    /**
     * Must return a virtual client, or null if the config does not support a virtual client.
     */
    async getVirtualClient(config) {
        return null;
    }
}