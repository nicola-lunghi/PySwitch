/**
 * Configuration loaded from local storage
 */
class PresetConfiguration extends Configuration {

    #id = null;
    
    constructor(controller, id, title = null) {
        if (!title) {
            title = id;
        }

        super(controller, title);
        this.#id = id;
    }

    /**
     * Loads config files from storage
     */
    async load() {
        if (!this.controller.presets.has(this.#id)) throw new Error("Preset " + this.#id + " not found");
        return this.controller.presets.get(this.#id);
    }

    /**
     * Can the config be saved?
     */
    canBeSaved() {
        return true;
    }
    
    /**
     * Save the data to the location of the configuration
     */
    async doSave() {
        await this.controller.presets.set(this.#id, await this.get());
    }
}