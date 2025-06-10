/**
 * Implements the display editor
 */
class DisplayEditor {
    
    #container = null;
    controller = null;

    #preview = null;
    #params = null;

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
        this.#container = $('<div class="display-editor" />')

        let previewContainer = null;
        this.#container.append(
            // Preview
            previewContainer = $('<div class="display-preview-container" />'),

            // Parameters
            $('<div class="display-parameters-container" />').append(
                await (this.#params = new DisplayEditorParameters(this.controller)).get()
            )
        );

        previewContainer.append(
            await (this.#preview = new DisplayEditorPreview(this, previewContainer)).get()
        );

        return this.#container;
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