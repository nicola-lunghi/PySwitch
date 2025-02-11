class Configuration {

    #data = null;
    #name = null;
    
    constructor(name = "") {
        this.#name = name;
    }

    /**
     * Returns an object containing all config code. Normally this is:
     * {
     *      inputs_py: "Code",
     *      display_py: "Code"
     * }
     */
    async get() {
        if (!this.loaded()) {
            this.#data = await this.load();
        }
        
        return this.#data;
    }

    /**
     * Returns a parser for the configuration
     */
    async parser(runner) {
        await this.get();
        return Parser.getInstance(this, runner);
    }

    /**
     * Returns if the config has been loaded
     */
    loaded() {
        return !!this.#data;
    }

    /**
     * Returns the text for the head line
     */
    async name() {
        return this.#name;
    }

    ///////////////////////////////////////////////////////////////////

    /**
     * Must load data and return it
     */
    async load() {
        throw new Error("Must be implemented in child classes");
    }

}