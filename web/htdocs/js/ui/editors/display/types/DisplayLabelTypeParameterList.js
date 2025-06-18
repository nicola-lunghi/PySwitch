class DisplayLabelTypeParameterList extends DisplayParameterList {
    
    #type = null; // Type handler

    constructor(type) {
        super(type.handler);
        this.#type = type;
    }
    /**
     * Sets up parameters on the passed ParameterList instance, according to the type of display element.
     */
    async setupTypeParameters() {
        await this.setupPositionParameters();
        await this.setupSizeParameters();

        await this.#setupScaleParameter();

        await this.#type.layout.setupParameters(this);

        await this.#setupSelectCallbackParameter();
    }

    /**
     * Sets up the scale parameter
     */
    async #setupScaleParameter() {
        const that = this;
        await this.createNumericInput({
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
     * Sets up the select callback parameter
     */
    async #setupSelectCallbackParameter() {
        const valueNode = Tools.getArgument(this.handler.node, "callback");
        
        const options = [];
        for (const client of this.handler.editor.availableCallbacks) {
            for(const cb of client.callbacks || []) {
                if (cb.target != "DisplayLabel") continue;
                
                options.push(
                    $('<option />')
                        .prop('value', cb.name)
                        .text(cb.name)
                )
            }
        }

        let select = null;

        const that = this;
        await this.createTextInput({
            name: "callback",
            comment: "Optional callback. This is used to set the label text independent of an action. If you set the label in a 'display' parameter of an action, this is NOT necessary!",
            displayName: "Callback",
            value: valueNode ? valueNode.value.name : "None",
            additionalClasses: "wide",
            onChange: async function(value) {
                that.setParameter('callback', value);
                await that.#setCallback(value);                
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
                            const value = select.val();
                            if (value == "") return;

                            that.setParameter('callback', value);
                            await that.#setCallback(value)

                        } catch(e) {
                            that.handler.editor.controller.handle(e);
                        }
                    })
            ]
        });
    }

    /**
     * Updates the parameters on the passed ParameterList instance according to the node.
     */
    updateTypeParameters() {
        // Bounds
        const bounds = this.handler.getModelBounds();
        this.setParameter('x', bounds.x);
        this.setParameter('y', bounds.y);
        this.setParameter('width', bounds.width);
        this.setParameter('height', bounds.height);
    }

    /**
     * Sets a new callback on the data model, if changed.
     */
    async #setCallback(name) {
        const current = this.handler.getParameter('callback');

        // Only set if changed
        if (current && current.name == name) return;

        if (!name) {
            this.handler.setParameter('callback', 'None');
            await this.handler.editor.parameters.rebuild();
            return;
        }

        const definition = await this.handler.editor.getConfig().parser.getCallbackDefinition(name);

        if (!definition) {
            this.handler.setParameter('callback', {
                name: name,
                arguments: []
            });
            await this.handler.editor.parameters.rebuild();
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
        
        await this.handler.editor.parameters.rebuild();
    }
}