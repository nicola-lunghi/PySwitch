class VirtualKemperParameters {

    #client = null;
    #data = null;
    #defaults = [];

    constructor(client) {
        this.#client = client;
        this.#data = new Map();
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
    
    /**
     * Returns the value for the key, or 0 if not found
     */
    value(key) {
        const entry = this.get(key);
        if (entry) return entry.config.value;

        return 0;
    }

    /**
     * Returns the entry of the parameter (if known), or null
     */
    get(key) {
        const jsonKey = key.getId();
        return this.#data.has(jsonKey) ? this.#data.get(jsonKey) : null
    }

    /**
     * Sets the value for the given key.
     */
    set(key, value) {
        let param = this.get(key);
        if (!param) {
            param = this.init({ key: key, value: value });
        }

        param.config.value = value;

        // Send message
        param.send();
    }

    /**
     * Initializes a parameter value.
     */
    init(config) {
        const jsonKey = config.key.getId();
        
        const param = new VirtualKemperParameter(
            this.#client, 
            config
        );

        this.#data.set(
            jsonKey, 
            param
        );

        return param;
    }

    /**
     * Initializes a default for a value type.
     */
    initDefault(config) {
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
}