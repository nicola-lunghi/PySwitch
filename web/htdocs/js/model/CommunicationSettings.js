/**
 * Handles global comm configuration
 */
class CommunicationSettings {

    #state = null;
    #defaults = null;

    constructor() {
        this.#state = new LocalState("global-settings");
        this.#defaults = {
            inChannel: null,
            outChannel: 0,
            debug: false
        }
    }

    /**
     * Get the configuration
     */
    get() {
        return this.#state.get("communication") || {}
    }

    /**
     * Set the configuration
     */
    set(data) {
        this.#state.set("communication", data || {})
    }

    /**
     * Returns a single value
     */
    getAttribute(name) {
        const data = this.get();

        if (data.hasOwnProperty(name)) return data[name];

        if (!this.#defaults.hasOwnProperty(name)) return null;
        return this.#defaults[name];
    }

    /**
     * Sets a single value
     */
    setAttribute(name, value) {
        const data = this.get();

        data[name] = value;
        
        this.set(data);
    }
}