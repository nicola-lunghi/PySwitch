class Parser {

    config = null;

    constructor(config) {
        this.config = config;
    }

    static async getInstance(config) {
        return new KemperParser(config);
    }

    /**
     * Returns the class(es) to set on the device element
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
}