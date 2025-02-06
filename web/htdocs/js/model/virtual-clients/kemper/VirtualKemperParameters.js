class VirtualKemperParameters {

    #client = null;
    #data = null;
    #defaults = [];
    #callbacks = [];

    constructor(client) {
        this.#client = client;
        this.#data = new Map();
    }

    /**
     * Adds a callback after init()
     * 
     * callback(param) => void
     */
    addInitCallback(callback) {
        this.#callbacks.push(callback);
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
        const jsonKey = key.getId();
        if (!this.#data.has(jsonKey)) return 0;

        const entry = this.#data.get(jsonKey);
        return entry.value;
    }

    /**
     * Returns the entry of the parameter (if known). Will be created if not present.
     */
    get(key) {
        const jsonKey = key.getId();

        if (!this.#data.has(jsonKey)) {
            return this.init({ keys: new VirtualKemperParameterKeys({ send: key }), value: 0 });
        }

        return this.#data.get(jsonKey);
    }

    /**
     * Initializes a parameter value.
     */
    init(config) {
        const jsonKey = config.keys.getId();
        
        if (this.#data.has(jsonKey)) {
            throw new Error("Redundant parameter definition: " + jsonKey);
        }

        const param = new VirtualKemperParameter(
            this.#client, 
            config
        );

        this.#data.set(
            jsonKey, 
            param
        );

        for (const cb of this.#callbacks) {
            cb(param);
        }

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

    destroy() {
        this.#data = new Map();
    }
}