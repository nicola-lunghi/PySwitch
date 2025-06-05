/**
 * Implements the display editor
 */
class DisplayEditor {
    
    #preview = null;
    container = null;
    controller = null;

    constructor(controller) {
        this.controller = controller;        
    }
    
    destroy() {
        if (this.#preview) {
            this.#preview.destroy();
        }
    }

    /**
     * Generate the DOM for the properties panel, or null if no options are present.
     */
    async get() {
        this.container = $('<div class="display-editor" />')

        this.container.append(
            await (this.#preview = new DisplayEditorPreview(this)).get()
        )

        return this.container;
    }

    /**
     * Apply the changes to the current config
     */
    async apply() {
        const newSplashes = await this.#preview.createSplashes();
        const parser = this.getConfig().parser;

        await this.controller.restart({
            message: "none",
            changeCallback: async function() {
                await parser.setSplashes(newSplashes);
            }
        });
    }

    /**
     * Called after get()
     */
    async init() {
        await this.#preview.init();
    }

    /**
     * Returns the configuration to use
     */
    getConfig() {
        return this.controller.currentConfig;
    }
}