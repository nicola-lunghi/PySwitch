/**
 * Implements the display editor
 */
class DisplayEditorPreview {
    
    #editor = null;
    #element = null;
    #rootNode = null;   // Raw data tree

    scaleFactor = 1;
    root = null;        // Root node handler
    references = null;  // Memory for node references
    
    selected;           // Selected node handler (managed by the node handlers)

    controller = null;

    constructor(editor) {
        this.#editor = editor;
        this.controller = editor.controller;
    }
    
    /**
     * Generate the DOM for the properties panel, or null if no options are present.
     */
    async get() {
        return this.#element = $('<div class="display-preview" />');
    }

    /**
     * Returns a new splashes object to be set on the configuration
     */
    async createSplashes() {
        const splashes = JSON.parse(JSON.stringify(this.#editor.getConfig().parser.splashes()));

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
     * Called after get()
     */
    async init() {
        // Get raw splashes tree (deep copy, because we do not want to alter the parser data yet)
        this.#rootNode = JSON.parse(JSON.stringify(await this.#getRootNode()));

        // Get scale factor (determined by the device)
        this.scaleFactor = await this.#determineScaleFactor();

        // Root dimensions
        const displayDimensions = (await Device.getInstance(this.#editor.getConfig())).getDisplayDimensions();
        this.#element
            .width(displayDimensions[0] * this.scaleFactor)
            .height(displayDimensions[1] * this.scaleFactor);

        await this.#update();
    }

    /**
     * Returns the root node for the editor
     */
    async #getRootNode() {
        const splashes = this.#editor.getConfig().parser.splashes();

        // The root element may be client dependent
        const client = ClientFactory.getInstance(splashes.client ? splashes.client : "local");

        // Get raw splashes tree (deep copy, because we do not want to alter the parser data yet)
        return client.getSplashesRootElement(splashes);
    }

    /**
     * Update the editor to the current state
     */
    async #update() {
        // Clear
        this.#element.empty();
        this.references = new Map();

        // Create root
        this.root = new DisplayEditorPreviewNode(
            this,
            this.#rootNode
        );

        // Render elements
        this.#element.append(this.root.initElement());

        // Init after the hierarchy is set up
        this.root.init();
    }

    /**
     * Determines scale factor and sets it. Returns the display dimensions on screen.
     */
    async #determineScaleFactor() {
        // const displayDimensions = (await Device.getInstance(config)).getDisplayDimensions();
        // const displayWidth = displayDimensions[0];
        // const displayHeight = displayDimensions[1];

        return 2;
        // TODO
        

        // const availableWidth = this.#container.width()
        // const availableHeight = this.#container.height()

        // if (availableHeight < availableWidth) {
        //     this.#scaleFactor = availableHeight / displayHeight;
        //     return availableHeight - 2;
        // } else {
        //     this.#scaleFactor = availableWidth / displayWidth;
        //     return availableWidth - 2;
        // }
    }
}