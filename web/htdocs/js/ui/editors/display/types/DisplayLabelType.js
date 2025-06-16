class DisplayLabelType extends DisplayNodeType {

    layout = null;    // DisplayLabelTypeLayout instance

    constructor(handler) {
        super(handler);

        this.layout = new DisplayLabelTypeLayout(handler)
    }

    /**
     * Sets up the preview DOM element
     */
    setupPreviewElement(element) {
        element.addClass('display-label')
    }

    /**
     * Is the node editable?
     */
    editable() {
        return true;
    }

    /**
     * Returns if the node is resizable
     */
    resizable() {
        return true;
    }

    /**
     * Returns the display text for the node (for all others than the preview)
     */
    getName() {
        if (this.handler.node.hasOwnProperty("assign")) return this.handler.node.assign;

        const callback = Tools.getArgument(this.handler.node, "callback");
        if (callback) return callback.value.name;
        
        return super.getName();
    }

    /**
     * Background color for preview or null for no specific color is wanted
     */
    getPreviewBackColor() {
        return this.layout.getParameter('backColor');
    }

    /**
     * Text color for preview or null for no specific color is wanted
     */
    getPreviewTextColor() {
        return this.layout.getParameter('textColor');
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Sets up parameters on the passed ParameterList instance, according to the type of display element.
     */
    async setupParameters(list) {
        await list.setupPositionParameters();
        await list.setupSizeParameters();

        await this.#setupScaleParameter(list);

        await this.layout.setupParameters(list);
    }

    /**
     * Sets up the scale parameter
     */
    async #setupScaleParameter(list) {
        const valueNode = Tools.getArgument(this.handler.node, "scale");
        const that = this;
        await list.createNumericInput({
            name: "scale",
            comment: "Scale the text in the label. NOTE: If you have a Max. Text Width set, you have to adapt it by the same factor.",
            displayName: "Scale by",
            value: valueNode ? valueNode.value : 1,
            range: {
                min: 1
            },
            onChange: async function(value) {
                if (value == 1) {
                    // Remove parameter
                    that.handler.node.arguments = that.handler.node.arguments.filter((entry) => (entry.name != 'scale'));

                } else {
                    // Set/add parameter
                    let valueNode2 = Tools.getArgument(that.handler.node, 'scale');
                    if (!valueNode2) {
                        that.handler.node.arguments.push(valueNode2 = {
                            name: 'scale'
                        })
                    }
                    valueNode2.value = value;
                }
            }
        });
    }

    /**
     * Updates the parameters on the passed ParameterList instance according to the node.
     */
    updateParameters(list) {
        // Bounds
        const bounds = this.handler.getModelBounds();
        list.setParameter('x', bounds.x);
        list.setParameter('y', bounds.y);
        list.setParameter('width', bounds.width);
        list.setParameter('height', bounds.height);

        // Colors
        //list.setParameter('backColor', this.layout.getParameter('backColor'));
        //list.setParameter('textColor', this.layout.getParameter('textColor'));
    }
}