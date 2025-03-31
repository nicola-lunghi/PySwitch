class Presets {

    #state = null;

    constructor() {
        this.#state = new LocalState("presets", true); // No PySwitch version
    }

    /**
     * Returns a list of all preset ids available
     */
    getAll() {
        const presets = this.#state.get("data") || [];

        return presets.map((item) => item.id);
    }

    /**
     * Does the preset exist?
     */
    has(id) {
        return !!this.get(id);
    }

    /**
     * Gets preset data by ID
     */
    get(id) {
        const presets = this.#state.get("data") || [];

        for (const preset of presets) {
            if (preset.id == id) {
                return preset.data;
            }
        }

        return null;
    }

    /**
     * Sets or adds a preset
     */
    set(id, data) {
        let presets = this.#state.get("data") || [];

        // Remove old
        presets = presets.filter((item) => item.id != id);

        // Add
        presets.push({
            id: id,
            data: data
        });

        this.#state.set("data", presets);
    }

    /**
     * Delete an entry
     */
    delete(id) {
        let presets = this.#state.get("data") || [];

        presets = presets.filter((item) => item.id != id);

        this.#state.set("data", presets);
    }
}