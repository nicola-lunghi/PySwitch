class Presets {

    #state = null;

    constructor() {
        this.#state = new LocalState("pyswitch-presets");
    }

    /**
     * Returns a list of all preset ids available
     */
    getAll() {
        const presets = this.#state.get("data");

        return ["foo"];
    }

    /**
     * Gets preset data by ID
     */
    get(id) {
        return null;
    }

    /**
     * Sets or adds a preset
     */
    set(id, data) {

    }
}