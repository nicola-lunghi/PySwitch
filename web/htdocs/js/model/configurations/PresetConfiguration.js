/**
 * Configuration loaded from local storage
 */
class PresetConfiguration extends Configuration {

    #id = null;
    #presets = null;
    
    constructor(presets, id, title = null) {
        if (!title) {
            title = id;
        }

        super(title);
        this.#id = id;
        this.#presets = presets;

    }

    /**
     * Loads config files from storage
     */
    async load() {
        if (!this.#presets.has(this.#id)) throw new Error("Preset " + this.#id + " not found");
        return this.#presets.get(this.#id);
    }
}