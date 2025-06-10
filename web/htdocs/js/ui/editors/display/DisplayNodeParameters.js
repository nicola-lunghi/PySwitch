class DisplayNodeParameters {
    
    element = null;
    #handler = null;

    #inputs = null;

    constructor(handler) {
        this.#handler = handler;

        this.#inputs = new DisplayNodeParameterList(handler);
    }

    async destroy() {
    }

    /**
     * Sets up the element
     */
    async setup() {
        let inner = null;
        this.element = $('<div class="display-parameters-item" />').append(
            inner = $('<div class="display-parameters" />')
        )
        
        switch(this.#handler.node.name) {
            case "DisplayLabel":
                this.#renderDisplayLabel(inner);
                break;
        }

        // Label text
        const text = this.#handler.getText();
        inner
            .text(text)
            .attr('data-toggle', 'tooltip')
            .attr('title', text);

        // Add parameters
        //inner.append(await this.#inputs.get());
    }

    setSelected(selected) {
        this.element.children().toggleClass('selected', selected);
    }    

    /**
     * Renders a DisplayLabel node. Returns DOM.
     */
    #renderDisplayLabel(element) {
        const that = this;
        element
            .addClass('display-label')
            .on('click', async function() {
                try {
                    that.#handler.select();
                    
                } catch (e) {
                    that.#handler.editor.controller.handle(e);
                }
            })
    }

    init() {        
    }

    update() {
        // Bounds
        const bounds = this.#handler.getModelBounds();
    
        // this.#inputs.set('x', bounds.x);
        // this.#inputs.set('y', bounds.y);
        // this.#inputs.set('w', bounds.width);
        // this.#inputs.set('h', bounds.height);


        // // Order
        // this.element.css('z-index', this.#handler.getChildIndex());
    }
}