class ParameterList {

    controller = null;
    #inputs = [];

    constructor(controller) {
        this.controller = controller;
    }

    /**
     * Generate the DOM for the properties panel, or null if no options are present.
     */
    async get() {
        this.#inputs = [];
        await this.setup();

        const rows = this.#getRows();
        const headline = await this.getHeadline();

        return $('<span class="parameter-list-container" />').append(
            $('<div class="parameter-list" />').append(
                !headline ? null :
                $('<div class="parameter-comment" />')
                .html(headline),

                !rows ? null :
                $('<div class="parameters" />').append(
                    $('<table />').append(
                        $('<tbody />').append(
                            rows
                        )
                    )
                )
            )
        )
    }

    /**
     * Can return a headline
     */
    async getHeadline() {
        return null;
    }

    /**
     * Must set up all inputs by calling the create* methods.
     */
    async setup() {
        // Implement in child classes to set up the inputs
    }
    
    ///////////////////////////////////////////////////////////////////////////////////////

    /**
     * Creates a boolean input. Options:
     * 
     * {
     *     name,
     *     displayName, (optional, default: name)
     *     comment,
     *     value,
     *     onChange: async (checked) => void (optional),
     *     additionalContent: Additional DOM content (optional)
     *     commentPlacement: Tippy placement option (default: top-end)
     * }
     */
    createBooleanInput(options) {
        options.type = 'checkbox';        
        options.getValue = (input) => !!input.prop('checked');
        options.setValue = (input, value) => input.prop('checked', value);

        this.createInput(options);
    }

    /**
     * Creates a boolean input. Options:
     * 
     * {
     *     name,
     *     displayName, (optional, default: name)
     *     comment,
     *     value,
     *     onChange: async (value) => void (optional),
     *     additionalContent: Additional DOM content (optional)
     *     commentPlacement: Tippy placement option (default: top-end)
     * }
     */
    createNumericInput(options) {
        options.type = 'number';

        this.createInput(options);
    }

    /**
     * Creates a text input. Options:
     * 
     * {
     *     name,
     *     displayName, (optional, default: name)
     *     comment,
     *     value,
     *     onChange: async (value) => void (optional),
     *     additionalContent: Additional DOM content (optional)
     *     commentPlacement: Tippy placement option (default: top-end)
     * }
     */
    createTextInput(options) {
        options.type = 'text';

        this.createInput(options);
    }

    /**
     * Creates an input. Options:
     * 
     * {
     *     type,
     *     name,
     *     displayName, (optional, default: name)
     *     comment,
     *     value,
     *     getValue: (input) => value (optional, default is .val())
     *     setValue: (input, value) => void (optional, default is val())
     *     onChange: async (value) => void (optional),
     *     additionalContent: Additional DOM content (optional),
     *     commentPlacement: Tippy placement option (default: top-end)
     * }
     */
    createInput(options) {
        const that = this;

        let input = null;
        const inputCell = $('<td />').append(
            input = $('<input />')
            .on('change', async function() {
                try {
                    if (options.onChange) {
                        const value = options.getValue ? options.getValue($(this)) : $(this).val();
                        await options.onChange(value);
                    }
                
                } catch (e) {
                    that.controller.handle(e);
                }
            })
            .prop('type', options.type)
            .prop('name', options.name),
            
            options.additionalContent
        )

        if (options.setValue) {
            options.setValue(input, options.value);
        } else {
            input.val(options.value);
        }

        if (!options.onChange) {
            input.prop('readonly', true);
        }

        this.#inputs.push({
            type: options.type,
            name: options.name,
            row: Tools.withComment(
                $('<tr />').append(                            
                    $('<td />').append(
                        $('<span />').text(options.displayName ? options. displayName : options.name)
                    ),

                    inputCell
                ),
                options.comment,
                options.commentPlacement ? options.commentPlacement : "top-end"
            ),
            input: input
        })
    }

    ///////////////////////////////////////////////////////////////////////////

    /**
     * Sets the value of a parameter
     */
    set(name, value) {
        for(const input of this.#inputs) {
            if (input.name == name) {
                input.input.val(value);
                return;
            }
        }

        throw new Error("Parameter " + name + " not found")
    }

    ///////////////////////////////////////////////////////////////////////////

    /**
     * Returns an array of option rows
     */
    #getRows() {
        const ret = [];
        for (const input of this.#inputs) {
            ret.push(input.row);
        }
        return ret;
    }
}