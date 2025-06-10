/**
 * Implements the display editor
 */
class DisplayEditorPreview {
    
    #editor = null;
    #element = null;
    #container = null;
    #rootNode = null;   // Raw data tree

    scaleFactor = 1;
    root = null;        // Root node handler
    references = null;  // Memory for node references
    
    selected;           // Selected node handler (managed by the node handlers)
    #resizeObserver = null;
    #resizeUpdateHandle = null;

    controller = null;

    constructor(editor, container) {
        this.#editor = editor;
        this.controller = editor.controller;
        this.#container = container;
    }

    /**
     * Destroy the preview
     */
    destroy() {
        if (this.#resizeObserver) {
            this.#resizeObserver.disconnect();
        }
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
        this.#rootNode = JSON.parse(JSON.stringify(await this.#createRootNode()));

        await this.#update();

        this.#initResizeObserver();
    }

    /**
     * When the parent is resized, we want to recalculate
     */
    #initResizeObserver() {
        const that = this;
        this.#resizeObserver = new ResizeObserver(async (entries) => {
            if (that.#resizeUpdateHandle) {
                clearTimeout(that.#resizeUpdateHandle);
            }

            that.#resizeUpdateHandle = setTimeout(async () => {
                await that.#update();
            }, 100)            
        });

        this.#resizeObserver.observe(this.#editor.controller.ui.container[0]);
    }

    /**
     * Returns the root node for the editor
     */
    async #createRootNode() {
        const splashes = this.#editor.getConfig().parser.splashes();

        // The root element may be client dependent
        const client = ClientFactory.getInstance(splashes.client ? splashes.client : "local");

        // Get raw splashes tree (deep copy, because we do not want to alter the parser data yet)
        return client.getSplashesRootElement(splashes);
    }

    /**
     * Update the editor to the current state of the model
     */
    async #update() {
        // Clear
        this.selected = null;
        if (this.root) this.root.destroy();
        this.references = new Map();
        this.#element
            .empty()
            .css('width', 'unset')
            .css('height', 'unset');
        
        // Get scale factor (determined by the device)
        this.scaleFactor = await this.#determineScaleFactor();

        // Root element dimensions
        const displayDimensions = (await Device.getInstance(this.#editor.getConfig())).getDisplayDimensions();   // 240x240
        this.#element
            .width(displayDimensions[0] * this.scaleFactor)
            .height(displayDimensions[1] * this.scaleFactor);

        // Create root
        this.root = new DisplayEditorPreviewNode(
            this,
            this.#rootNode
        );

        // Render elements
        this.#element.append(this.root.setup());

        // Init after the hierarchy is set up
        this.root.init();
    }

    /**
     * Determines scale factor and sets it. Returns the display dimensions on screen.
     */
    async #determineScaleFactor() {
        // Display (240x240)
        const displayDimensions = (await Device.getInstance(this.#editor.getConfig())).getDisplayDimensions();
        const displayWidth = displayDimensions[0];
        const displayHeight = displayDimensions[1];
        const displayRatio = displayWidth / displayHeight;

        // Container size
        const availableWidth = this.#container.width() - 3
        const availableHeight = this.#container.height() - 3
        const availableRatio = availableWidth / availableHeight;

        if (availableRatio > displayRatio) {
            // Available is wider than the display: Height counts
            return availableHeight / displayHeight;
        } else {
            // Display is wider than available: Width counts
            return availableWidth / displayWidth;
        }
    }
}