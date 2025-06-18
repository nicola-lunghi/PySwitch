class BidirectionalStateTypeParameterList extends DisplayParameterList {
    
    constructor(handler) {
        super(handler);
    }
    /**
     * Sets up parameters on the passed ParameterList instance, according to the type of display element.
     */
    async setupTypeParameters() {
        await this.setupPositionParameters();
    }

    /**
     * Updates the parameters on the passed ParameterList instance according to the node.
     */
    updateTypeParameters() {
        // Bounds
        const bounds = this.handler.getModelBounds();
        this.setParameter('x', bounds.x);
        this.setParameter('y', bounds.y);
    }
}