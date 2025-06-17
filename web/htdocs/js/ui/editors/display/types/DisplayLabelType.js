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

        await this.#setupCallbackParameters(list);
    }

    /**
     * Sets up the scale parameter
     */
    async #setupScaleParameter(list) {
        const that = this;
        await list.createNumericInput({
            name: "scale",
            comment: "Scale the text in the label. NOTE: If you have a Max. Text Width set, you have to adapt it by the same factor.",
            displayName: "Scale by",
            value: this.handler.getParameter('scale', 1),
            range: {
                min: 1
            },
            onChange: async function(value) {
                that.handler.setParameter('scale', value, 1);
            }
        });
    }

    /**
     * Sets up the callback parameters (select callback and the callback specific parameters)
     */
    async #setupCallbackParameters(list) {
        await this.#setupSelectCallbackParameter(list);
        await this.#setupCallbackSpecificParams(list);
    }
    
    /**
     * Sets up the select callback parameter
     */
    async #setupSelectCallbackParameter(list) {
        const valueNode = Tools.getArgument(this.handler.node, "callback");
        
        const availableCallbacks = await this.handler.editor.getConfig().parser.getAvailableDisplayLabelCallbacks();

        const options = [];
        for (const client of availableCallbacks) {
            for(const cb of client.callbacks || []) {
                options.push(
                    $('<option />')
                        .prop('value', cb.name)
                        .text(cb.name)
                )
            }
        }

        let select = null;

        const that = this;
        await list.createTextInput({
            name: "callback",
            comment: "Optional callback. This is used to set the label text independent of an action. If you set the label in a 'display' parameter of an action, this is NOT necessary!",
            displayName: "Callback",
            value: valueNode ? valueNode.value.name : "None",
            additionalClasses: "wide",
            onChange: async function(value) {
                await that.#setCallback(value);
                await list.rebuild();
            },
            additionalContent: [
                select = $('<select class="parameter-option" />')
                    .append(
                        $('<option />')
                        .prop('value', "")
                        .text('Select Callback...')                    
                    )
                    .append(options)
                    .on('change', async function() {
                        try {
                            await that.#setCallback(select.val())
                            await list.rebuild();

                        } catch(e) {
                            that.handler.editor.controller.handle(e);
                        }
                    })
            ]
        });
    }

    /**
     * Sets up parameters specific to the current callback
     */
    async #setupCallbackSpecificParams(list) {
        // Get current callback
        const current = this.handler.getParameter('callback');
        if (!current) return;

        // Get definition
        const definition = await this.handler.editor.getConfig().parser.getDisplayLabelCallbackDefinition(
            current.name,
            current.client
        );
        // console.log(definition)
        if (!definition) return;

        // Add parameters
        for(const param of definition.parameters) {
            const type = param.meta.type();

            // Get current value or default if not set
            const value = null; // TODO

            await list.createInput({
                type: list.convertType(type),
                name: param.name,
                comment: param.comment,
                value: value,
                onChange: async function(value) {
                    console.log(value) // TODO  
                }
            });
        }
    }

    /**
     * Sets a new callback on the data model, if changed.
     */
    async #setCallback(name) {
        const current = this.handler.getParameter('callback');

        // Only set if changed
        if (current && current.name == name) return;

        const definition = await this.handler.editor.getConfig().parser.getDisplayLabelCallbackDefinition(name);
        if (!definition) {
            this.handler.setParameter('callback', {
                name: name,
                arguments: []
            });
            return;
        }
        
        this.handler.setParameter('callback', {
            name: name,
            client: definition.meta.client.id,
            arguments: definition.parameters          // Only add params without defaults
                .filter((param) => !param.default)
                .map((param) => {
                    return {
                        name: param.name,
                        value: param.meta.getDefaultValue()
                    }
                })
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
    }
}