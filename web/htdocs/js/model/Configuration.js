class Configuration {

    // Code of the configuration
    inputs_py = null;
    display_py = null;

    constructor(name = "") {
        this.name = name;
    }

    /**
     * Returns the text for the head line
     */
    headline() {
        return this.name;
    }

    /**
     * Must load the data.
     */
    async load() {
        throw new Error("Must be implemented in child classes");
    }
}