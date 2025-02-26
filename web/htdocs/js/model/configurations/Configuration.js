/**
 * Represents a configuration, consisting of the files inputs.py and display.py.
 * Child classes must provide the more specific loading implementations.
 */
class Configuration {

    #data = null;
    #name = null;
    parser = null;
    
    constructor(name = "") {
        this.#name = name;
    }

    /**
     * Init the parser
     */
    async init(runner, basePath = "") {
        await this.get();
        
        this.parser = new Parser(this, runner, basePath);
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
     * Set new data.
     */
    set(data) {
        this.#data = data;
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