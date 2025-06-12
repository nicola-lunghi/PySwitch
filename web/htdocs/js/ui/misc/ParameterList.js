class ParameterList {

    controller = null;
    inputs = [];

    constructor(controller) {
        this.controller = controller;
    }

    /**
     * Can return a headline (implement in child classes)
     */
    async getHeadline() {
        return null;
    }

    /**
     * Sets up all inputs by calling the create* methods. Implement in child classes.
     */
    async setup() {        
    }
    
    ///////////////////////////////////////////////////////////////////////////////////////

    /**
     * Creates a boolean input.
     */
    createBooleanInput(options) {
        options.type = 'checkbox';        
        options.getValue = (input) => !!input.prop('checked');
        options.setValue = (input, value) => input.prop('checked', value);

        this.createInput(options);
    }

    /**
     * Creates a boolean input.
     */
    createNumericInput(options) {
        options.type = 'number';

        this.createInput(options);
    }

    /**
     * Creates a text input.
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
     *     onChange: async (value, setNewValueCallback) => any (optional)
     *     getValue: (input) => value (optional, default is .val())
     *     setValue: (input, value) => void (optional, default is val())
     *     additionalContent: Additional DOM content (optional),
     *     commentPlacement: Tippy placement option (default: top-end)
     * }
     */
    createInput(options) {
        const that = this;

        let input = null;
        let messages = null;

        const inputCell = $('<td />').append(
            input = $('<input />')
            .on('change', async function() {
                try {
                    if (options.onChange) {
                        const value = options.getValue ? options.getValue($(this)) : $(this).val();
                        await options.onChange(value, function(newValue) {
                            if (value == newValue) return;
                            
                            if (options.setValue) {
                                options.setValue(input, newValue);
                                return;
                            }
                            input.val(newValue);
                        });                        
                    }
                
                } catch (e) {
                    that.controller.handle(e);
                }
            })
            .prop('type', options.type)
            .prop('name', options.name),
            
            options.additionalContent,

            messages = $('<span class="parameter-check-messages" />')
        )

        if (options.setValue) {
            options.setValue(input, options.value);
        } else {
            input.val(options.value);
        }

        if (!options.onChange) {
            input.prop('readonly', true);
        }

        const log = {
            clear: function() {
                messages.empty();
                input.removeClass('error')
                input.removeClass('warning')
            },
            message: function(message, type = 'I') {
                switch(type) {
                    case 'E': return log.error(message);
                    case 'W': return log.warn(message);
                    default: return log.log(message);
                }
            },
            error: function(msg) {
                messages.append(
                    $('<span class="error" />')
                    .text(msg)
                )
                input.removeClass('warning')
                input.addClass("error")
            },
            warn: function(msg) {
                messages.append(
                    $('<span class="warning" />')
                    .text(msg)
                )
                if (!input.hasClass("error")) {
                    input.addClass("warning");
                }
            },
            log: function(msg) {
                messages.append(
                    $('<span class="info" />')
                    .text(msg)
                )
            }
        }

        this.inputs.push({
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
            input: input,
            log: log
        })
    }

    ///////////////////////////////////////////////////////////////////////////

    /**
     * Generate the DOM for the properties panel, or null if no options are present.
     */
    async get() {
        this.inputs = [];
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
     * Sets the value of a parameter
     */
    setParameter(name, value) {
        for(const input of this.inputs) {
            if (input.name == name) {
                input.input.val(value);
                return;
            }
        }

        throw new Error("Parameter " + name + " not found")
    }

    /**
     * Gets an input decriptor object for the given parameter name.
     */
    getParameter(name) {
        for(const input of this.inputs) {
            if (input.name == name) {
                return input;
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
        for (const input of this.inputs) {
            ret.push(input.row);
        }
        return ret;
    }
}