class DisplayNodePreview {
    
    element = null;
    #handler = null;
    #textElement = null;

    constructor(handler) {
        this.#handler = handler;
    }

    async destroy() {
        (new DisplayNodePreviewDrag(this.#handler.editor.preview, this.#handler)).kill();
    }

    /**
     * Sets up the element
     */
    async setup() {
        const that = this;
        this.element = $('<span class="display-element" />')
            .append(
                this.#textElement = $('<span class="display-element-text" />')
            )
            .on('click', async function() {
                try {
                    if (!that.#handler.type.editable()) return;

                    that.#handler.select();
                    
                } catch (e) {
                    that.#handler.editor.controller.handle(e);
                }
            });
        
        this.#handler.type.setupPreviewElement(this.element);
    }

    /**
     * Let the node appear selected (UI only, internal)
     */
    setSelected(selected) {
        this.element.toggleClass('selected', selected);
    }    

    /**
     * Called after DOM is ready
     */
    init() {
        if (this.#handler.type.editable()) {
            // Make editable
            (new DisplayNodePreviewDrag(this.#handler.editor.preview, this.#handler)).init();
        }
    }

    /**
     * Update according to data model
     */
    update() {
        if (!this.#handler.editor.preview.scaleFactor) throw new Error("Preview not initialized");

        // Bounds
        try {
            const bounds = this.#handler.getModelBounds();
        
            this.#setDisplayElementBounds({
                x: bounds.x * this.#handler.editor.preview.scaleFactor,
                y: bounds.y * this.#handler.editor.preview.scaleFactor,
                width: bounds.width * this.#handler.editor.preview.scaleFactor,
                height: bounds.height * this.#handler.editor.preview.scaleFactor,
            })

        } catch(e) {
            // console.warn(e);
            this.#setDisplayElementBounds({
                x: 0,
                y: 0,
                width: 0,
                height: 0
            });
        }

        // Order
        this.element.css('z-index', this.#handler.getChildIndex());

        // Text
        this.#updateText();

        // Errors / Warnings
        const messages = this.#handler.getMessages();
        this.element.toggleClass('error', messages.filter((item) => (item.type == 'E')).length > 0);
        this.element.toggleClass('warning', messages.filter((item) => (item.type == 'W')).length > 0);
    }

    /**
     * Update the text according to the data model
     */
    #updateText() {
        const text = this.#handler.type.getPreviewText();
        this.#textElement
            .text(text)
            .attr('data-toggle', 'tooltip')
            .attr('title', text);
    }

    /**
     * Retunrs the bounds of a display element
     *
    #getDisplayElementBounds() {
        return {
            x: parseFloat(this.previewElement.css('left')),
            y: parseFloat(this.previewElement.css('top')),
            width: parseFloat(this.previewElement.css('width')),
            height: parseFloat(this.previewElement.css('height'))
        }
    }

    /**
     * Sets the bounds of a display element (model coords)
     */
    #setDisplayElementBounds(bounds) {
        this.element
            .css('left', bounds.x + "px")
            .css('top', bounds.y + "px")
            .css('width', bounds.width + "px")
            .css('height', bounds.height + "px")
    }
}