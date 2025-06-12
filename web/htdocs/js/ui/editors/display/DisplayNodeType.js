/**
 * Implements type specific stuff for DisplayNode
 */
class DisplayNodeType {

    #handler = null;   // DisplayNode instance

    constructor(handler) {
        this.#handler = handler;
    }
    
    /**
     * Called to set up the node handler
     */
    async setup() {
        switch(this.#handler.node.name) {
            case "BidirectionalProtocolState": 
                // Recalculate size for the state dot if not yet done.
                this.#recalculateDotSize(8, 8);
                break;
        }
    }

    /**
     * Recalculates the bounds for a typical dot element in PySwitch. These are placed 
     * at the top right corner of the bounds, with fixed size. For the editor, we 
     * recalculate that to the correct dot size.
     */
    #recalculateDotSize(width, height, internalMargin) {
        const bounds = this.#handler.getModelBounds();
        if (bounds.width == width && bounds.height == height) return;

        console.log(" -> Recalculate dot bounds for " + this.#handler.node.name);

        bounds.x += bounds.width - width;
        //bounds.y += internalMargin;
        bounds.width = width;
        bounds.height = height;

        this.#handler.setModelBounds(bounds);
    }

    /**
     * Sets up the preview DOM element
     */
    setupPreviewElement(element) {
        switch(this.#handler.node.name) {
            case "DisplayLabel":
                element.addClass('display-label')
                break;
            case "BidirectionalProtocolState":
                element.addClass('display-dot')
                break;
        }
    }

    /**
     * Is the node editable?
     */
    editable() {
        switch(this.#handler.node.name) {
            case "DisplayLabel": return true;
            case "BidirectionalProtocolState": return true;
        }
        return false;
    }

    /**
     * Returns if the node is resizable
     */
    resizable() {
        switch(this.#handler.node.name) {
            case "DisplayLabel": return true;
        }
        return false;
    }

    /**
     * Determines the bounds node from the data model.
     */
    getBoundsNode() {
        const ret = Tools.getArgument(this.#handler.node, "bounds");
        if (ret) return ret.value;

        if (this.#handler.node.arguments.length == 1) {
            if (this.#handler.node.arguments[0].value && 
                this.#handler.node.arguments[0].value.name == "DisplayBounds") {
                    
                return this.#handler.node.arguments[0].value;
            }
        }
        return null;
    }

    /**
     * Returns the display text for the node preview element
     */
    getPreviewText() {
        switch(this.#handler.node.name) {
            case "BidirectionalProtocolState":
                return "";
        }

        return this.getName();
    }

    /**
     * Returns the display text for the node (for all others than the preview)
     */
    getName() {
        if (this.#handler.node.hasOwnProperty("assign")) return this.#handler.node.assign;

        switch(this.#handler.node.name) {
            case "DisplayLabel":
                const callback = Tools.getArgument(this.#handler.node, "callback");
                if (callback) return callback.value.name;
                break;
        }

        return this.#handler.node.name;  
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Sets up parameters on the passed ParameterList instance, according to the type of display element.
     */
    async setupParameters(list) {
        switch (this.#handler.node.name) {
            case "DisplayLabel":
                await list.setupPositionParameters();
                await list.setupSizeParameters();
                break;

            case "BidirectionalProtocolState":
                await list.setupPositionParameters();
                break;
        }
    }

    /**
     * Updates the parameters on the passed ParameterList instance according to the node.
     */
    updateParameters(list) {
        const bounds = this.#handler.getModelBounds();
        switch (this.#handler.node.name) {
            case "DisplayLabel":
                list.setParameter('x', bounds.x);
                list.setParameter('y', bounds.y);
                list.setParameter('width', bounds.width);
                list.setParameter('height', bounds.height);
                break;

            case "BidirectionalProtocolState":
                list.setParameter('x', bounds.x);
                list.setParameter('y', bounds.y);
                break;
        }
    }
}