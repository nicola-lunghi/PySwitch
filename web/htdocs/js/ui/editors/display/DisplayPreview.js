/**
 * Display editor preview (where displays can be dragged around)
 */
class DisplayPreview {
    
    #editor = null;
    #element = null;
    #container = null;

    scaleFactor = 1;
    
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
    async destroy() {
        if (this.#resizeObserver) {
            await this.#resizeObserver.disconnect();
        }
    }
    
    /**
     * Generate the DOM for the properties panel, or null if no options are present.
     */
    async get() {
        return this.#element = $('<div class="display-preview" />');
    }

    /**
     * Called after get()
     */
    async init() {
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
                await that.#editor.reset();
            }, 100)            
        });

        this.#resizeObserver.observe(this.#editor.controller.ui.container[0]);
    }

    /**
     * Reset the editor to the current state of the model
     */
    async reset() {
        // Clear
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

        // Append to DOM
        this.#element.append(this.#editor.root.preview.element);
    }

    /**
     * Determines scale factor.
     */
    async #determineScaleFactor() {
        // Display (240x240)
        const displayDimensions = (await Device.getInstance(this.#editor.getConfig())).getDisplayDimensions();
        const displayWidth = displayDimensions[0];
        const displayHeight = displayDimensions[1];
        const displayRatio = displayWidth / displayHeight;

        // Container size
        const availableWidth = this.#container.width() //- 3
        const availableHeight = this.#container.height() //- 3
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