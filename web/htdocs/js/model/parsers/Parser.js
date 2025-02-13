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
     */
    async parse() {
        throw new Error("Must be implemented in child classes");
    }

    /**
     * Unparse a CST tree
     */
    async unparse() {
        throw new Error("Must be implemented in child classes");
    }

    /**
     * Returns an instance of Input.py
     * port must be an integer ID of the port (as defined in the board wrapper in python)
     */
    async input(port) {
        throw new Error("Must be implemented in child classes");
    }

    /**
     * Returns the class(es) to set on the device element
     */
    async getDeviceClass() {
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