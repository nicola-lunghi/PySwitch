/**
 * Configuration loaded from local storage
 */
class PresetConfiguration extends Configuration {

    #id = null;
    #controller = null;
    
    constructor(controller, id, title = null) {
        if (!title) {
            title = id;
        }

        super(title);
        this.#id = id;
        this.#controller = controller;

    }

    /**
     * Loads config files from storage
     */
    async load() {
        if (!this.#controller.presets.has(this.#id)) throw new Error("Preset " + this.#id + " not found");
        return this.#controller.presets.get(this.#id);
    }

    /**
     * Save the data to the location of the configuration
     */
    async save() {
        await this.#controller.presets.set(this.#id, await this.get());
    }
}