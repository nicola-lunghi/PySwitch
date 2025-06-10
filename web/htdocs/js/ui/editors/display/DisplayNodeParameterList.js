class DisplayNodeParameterList extends ParameterList {
    
    #handler = null;

    constructor(handler) {
        super(handler.editor.controller)
        this.#handler = handler;
    }

    async setup() {
        const bounds = this.#handler.getModelBounds();
        const that = this;

        this.createNumericInput(
            "x",
            "Vertical position",
            bounds.x,
            async function(value) {
                const bounds2 = that.#handler.getModelBounds();
                bounds2.x = value;
                that.#handler.setModelBounds(bounds2);
                
                that.#handler.update();
            }
        );

        this.createNumericInput(
            "y",
            "Horizontal position",
            bounds.y,
            async function(value) {
                const bounds2 = that.#handler.getModelBounds();
                bounds2.y = value;
                that.#handler.setModelBounds(bounds2);
                
                that.#handler.update();
            }
        );

        this.createNumericInput(
            "w",
            "Width",
            bounds.width,
            async function(value) {
                const bounds2 = that.#handler.getModelBounds();
                bounds2.width = value;
                that.#handler.setModelBounds(bounds2);
                
                that.#handler.update();
            }
        );

        this.createNumericInput(
            "h",
            "Height",
            bounds.height,
            async function(value) {
                const bounds2 = that.#handler.getModelBounds();
                bounds2.height = value;
                that.#handler.setModelBounds(bounds2);
                
                that.#handler.update();
            }
        );
    }
}