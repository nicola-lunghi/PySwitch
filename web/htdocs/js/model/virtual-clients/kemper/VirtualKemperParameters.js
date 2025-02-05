class VirtualKemperParameters {

    #client = null;
    #data = null;
    #defaults = [];

    constructor(client) {
        this.#client = client;
        this.#data = new Map();
    }

    /**
     * Returns the entry of the parameter (if known), or null
     */
    get(key) {
        const jsonKey = JSON.stringify(key);
        return this.#data.has(jsonKey) ? this.#data.get(jsonKey) : null
    }

    /**
     * Sets a value.
     */
    set(config) {
        const jsonKey = JSON.stringify(config.key);
        
        this.#data.set(
            jsonKey, 
            new VirtualKemperParameter(
                this.#client, 
                config
            )
        );
    }

    /**
     * Sets a default.
     */
    setDefault(config) {
        this.#defaults.push(
            new VirtualKemperParameterDefault(
                this.#client, 
                config
            )
        );
    }

    /**
     * Returns all parameters of a parameter set as array
     */
    getParameterSet(parameterSet) {
        const ret = [];
        for (const [key, entry] of this.#data) {
            if (entry.config.parameterSets && entry.config.parameterSets.includes(parameterSet)) {
                ret.push(entry);
            }
        }
        return ret;
    }

    /**
     * Try to parse all parameters. Returns if successful.
     */
    parse(message) {
        // Try all parameters
        for (const [key, entry] of this.#data) {
            if (entry.parse(message)) return true;
        }

        // Not parsed: Try defaults
        for (const def of this.#defaults) {
            if (def.parse(message)) return true;
        }

        return false;
    }
}