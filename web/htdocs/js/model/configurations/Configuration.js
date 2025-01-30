class Configuration {

    #data = null;
    #parser = null;
    
    constructor(name = "") {
        this.name = name;
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
    async parser() {
        await this.get();
        return Parser.getInstance(this);
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
    async headline() {
        return this.name;
    }

    ///////////////////////////////////////////////////////////////////

    /**
     * Must load data and return it
     */
    async load() {
        throw new Error("Must be implemented in child classes");
    }

}