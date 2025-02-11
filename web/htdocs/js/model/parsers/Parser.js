class Parser {

    config = null;

    constructor(config) {
        this.config = config;
    }

    static getInstance(config) {
        return new KemperParser(config);
    }

    /**
     * Returns a CST (Concrete Syntax Tree) from the sources.
     * Expects the PySwitchRunner.
     */
    async parse(runner) {
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