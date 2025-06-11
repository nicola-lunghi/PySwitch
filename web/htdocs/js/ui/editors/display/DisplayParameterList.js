/**
 * Generates a parameter list for a DisplayNode
 */
class DisplayParameterList extends ParameterList {
    
    #handler = null;  // DisplayNode instance

    constructor(handler) {
        super(handler.editor.controller)
        this.#handler = handler;
    }

    /**
     * Sets up the parameters
     */
    async setup() {
        // Order
        this.#setupOrderParameter();
        this.#setupAssignParameter();

        // Others, depending on the type of node
        this.#handler.type.setupParameters(this);
    }

    /**
     * Update inputs from the data model
     */
    update() {
        // Order
        this.set('z', this.#handler.getChildIndex());

        // Others, depending on the type of node
        this.#handler.type.updateParameters(this);
    }

    ////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Add Z parameter
     */
    async #setupOrderParameter() {
        const that = this;

        this.createNumericInput({
            name: "z",
            displayName: "Depth",
            //comment: "Z-Index (depth order index)",
            value: this.#handler.getChildIndex(),
            additionalContent: [
                // Move up button
                $('<span class="button fas fa-chevron-up" data-toggle="tooltip" title="Move up in depth" />')
                .on('click', async function() {
                    try {
                        that.#handler.moveUp();

                    } catch (e) {
                        that.controller.handle(e);
                    }
                }),

                // Move down button
                $('<span class="button fas fa-chevron-down" data-toggle="tooltip" title="Move down in depth" />')
                .on('click', async function() {
                    try {
                        that.#handler.moveDown();

                    } catch (e) {
                        that.controller.handle(e);
                    }
                })
            ]
        });
    }

    /**
     * Add assignment parameter
     */
    async #setupAssignParameter() {
        const that = this;

        this.createTextInput({
            name: "assign",
            displayName: "Export as",
            comment: "If you assign a name here, the label can be used in the actions. (This creates an assignment for the label instance which can be exported)",
            value: that.#handler.node.assign ? that.#handler.node.assign : "",
            onChange: async function(value) {
                that.#handler.node.assign = value;

                that.#handler.update();
                that.#handler.editor.parameters.update();
            }
        });
    }

    /**
     * Add x and y parameters
     */
    async setupPositionParameters() {
        const bounds = this.#handler.getModelBounds();
        const that = this;

        this.createNumericInput({
            name: "x",
            displayName: "X",
            //comment: "Vertical position",
            value: bounds.x,
            onChange: async function(value) {
                const bounds2 = that.#handler.getModelBounds();
                bounds2.x = value;
                that.#handler.setModelBounds(bounds2);
                
                that.#handler.update();
            }
        });

        this.createNumericInput({
            name: "y",
            displayName: "Y",
            //comment: "Horizontal position",
            value: bounds.y,
            onChange: async function(value) {
                const bounds2 = that.#handler.getModelBounds();
                bounds2.y = value;
                that.#handler.setModelBounds(bounds2);
                
                that.#handler.update();
            }
        });
    }

    /**
     * Add width and height parameters
     */
    async setupSizeParameters() {
        const bounds = this.#handler.getModelBounds();
        const that = this;

        this.createNumericInput({
            name: "width",
            displayName: "Width",
            //comment: "Width",
            value: bounds.width,
            onChange: async function(value) {
                const bounds2 = that.#handler.getModelBounds();
                bounds2.width = value;
                that.#handler.setModelBounds(bounds2);
                
                that.#handler.update();
            }
        });

        this.createNumericInput({
            name: "height",
            displayName: "Height",
            //comment: "Height",
            value: bounds.height,
            onChange: async function(value) {
                const bounds2 = that.#handler.getModelBounds();
                bounds2.height = value;
                that.#handler.setModelBounds(bounds2);
                
                that.#handler.update();
            }
        });
    }
}