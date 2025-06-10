/**
 * Implements the display editor
 */
class DisplayEditor {
    
    #container = null;
    controller = null;

    preview = null;
    parameters = null;

    #rootNode = null;    // Raw data tree
    root = null;         // Root node handler
    references = null;   // Memory for node references (node -> handler)
    selected;            // Selected node handler (managed by the node handlers themselves)

    constructor(controller) {
        this.controller = controller;        
    }
    
    async destroy() {
        if (this.preview) {
            await this.preview.destroy();
        }
        if (this.parameters) {
            await this.parameters.destroy();
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
            await (this.parameters = new DisplayParameters(this)).get()
        );

        previewContainer.append(
            await (this.preview = new DisplayPreview(this, previewContainer)).get()
        );

        return this.#container;
    }

    /**
     * Called after get()
     */
    async init() {
        // Get raw splashes tree (deep copy, because we do not want to alter the parser data yet)
        this.#rootNode = JSON.parse(JSON.stringify(await this.#createRootNode()));

        await this.reset();

        await this.preview.init();        
    }

    /**
     * Returns the root node for the editor
     */
    async #createRootNode() {
        const splashes = this.getConfig().parser.splashes();

        // The root element may be client dependent
        const client = ClientFactory.getInstance(splashes.client ? splashes.client : "local");

        // Get raw splashes tree (deep copy, because we do not want to alter the parser data yet)
        return client.getSplashesRootElement(splashes);
    }

    /**
     * Resets the app to the current data model, refreshing the display
     */
    async reset() {
        // Clear old handlers etc.
        this.selected = null;
        if (this.root) await this.root.destroy();

        this.references = new Map();
        await this.parameters.destroy();
        this.parameters.clear();
        
        // Create new root from the existing data model
        this.root = new DisplayNode(
            this,
            this.#rootNode
        );

        // Create element hierarchy
        await this.root.setup();

        // Attach to DOM
        await this.preview.reset();

        // Update view
        this.root.update();

        // Init interact.js etc. after the hierarchy is set up and attached
        this.root.init();

        await this.parameters.init();
    }

    /**
     * Apply the changes to the current config
     */
    async apply() {
        const newSplashes = await this.#createSplashes();
        const parser = this.getConfig().parser;

        await this.controller.restart({
            message: "none",
            changeCallback: async function() {
                await parser.setSplashes(newSplashes);
            }
        });
    }

    /**
     * Returns a new splashes object to be set on the configuration
     */
    async #createSplashes() {
        const splashes = JSON.parse(JSON.stringify(this.getConfig().parser.splashes()));

        // The root element may be client dependent
        const client = ClientFactory.getInstance(splashes.client ? splashes.client : "local");

        // Get raw splashes tree (deep copy, because we do not want to alter the parser data yet)
        if (await client.setSplashesRootElement(splashes, this.#rootNode)) {
            return splashes;
        }

        this.#rootNode.assign = "Splashes";

        return this.#rootNode;
    }

    /**
     * Returns the configuration to use
     */
    getConfig() {
        return this.controller.currentConfig;
    }
}