class BidirectionalProtocolStateType extends DisplayNodeType {
    
    /**
     * Called to set up the node handler
     */
    async setup() {
        // Recalculate size for the state dot if not yet done.
        this.#recalculateDotSize(8, 8);
    }

    /**
     * Recalculates the bounds for a typical dot element in PySwitch. These are placed 
     * at the top right corner of the bounds, with fixed size. For the editor, we 
     * recalculate that to the correct dot size.
     */
    #recalculateDotSize(width, height) {
        const bounds = this.handler.getModelBounds();
        if (bounds.width == width && bounds.height == height) return;

        console.log(" -> Recalculate dot bounds for " + this.handler.node.name);

        bounds.x += bounds.width - width;
        bounds.width = width;
        bounds.height = height;

        this.handler.setModelBounds(bounds);
    }

    /**
     * Sets up the preview DOM element
     */
    setupPreviewElement(element) {
        element.addClass('display-dot')
    }

    /**
     * Is the node editable?
     */
    editable() {
        return true;
    }

    /**
     * Returns the display text for the node preview element
     */
    getPreviewText() {
        return "";
    }

    /**
     * Returns the display text for the node (for all others than the preview)
     */
    getName() {
        if (this.handler.node.hasOwnProperty("assign")) return this.handler.node.assign;
        return this.handler.node.name;  
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Sets up parameters on the passed ParameterList instance, according to the type of display element.
     */
    async setupParameters(list) {
        await list.setupPositionParameters();
    }

    /**
     * Updates the parameters on the passed ParameterList instance according to the node.
     */
    updateParameters(list) {
        const bounds = this.handler.getModelBounds();
        list.setParameter('x', bounds.x);
        list.setParameter('y', bounds.y);
    }
}