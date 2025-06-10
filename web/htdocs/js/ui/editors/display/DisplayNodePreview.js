class DisplayNodePreview {
    
    element = null;
    #handler = null;

    constructor(handler) {
        this.#handler = handler;
    }

    async destroy() {
        (new DisplayNodeDrag(this.#handler.editor.preview, this.#handler)).kill();
    }

    /**
     * Sets up the element
     */
    async setup() {
        this.element = $('<span class="display-element" />');
        
        switch(this.#handler.node.name) {
            case "DisplayLabel":
                this.#renderDisplayLabel();
                break;
        }

        // Label text
        const text = this.#handler.getText();
        this.element
            .text(text)
            .attr('data-toggle', 'tooltip')
            .attr('title', text);
    }

    setSelected(selected) {
        this.element.toggleClass('selected', selected);
    }    

    /**
     * Renders a DisplayLabel node. Returns DOM.
     */
    #renderDisplayLabel() {
        const that = this;
        this.element
            .addClass('display-label')
            // .addClass('editable')
            .on('click', async function() {
                try {
                    that.#handler.select();
                    
                } catch (e) {
                    that.#handler.editor.controller.handle(e);
                }
            })
    }

    init() {
        if (this.#handler.editable) {
            // Make editable
            (new DisplayNodeDrag(this.#handler.editor.preview, this.#handler)).init();
        }
    }

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