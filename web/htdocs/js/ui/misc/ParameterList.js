class ParameterList {

    controller = null;
    inputs = [];
    parser = null;        // Only needed when a color input is used

    constructor(controller, parser = null) {
        this.controller = controller;
        this.parser = parser;
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
    async createBooleanInput(options) {
        options.type = 'checkbox';        
        options.getValue = (input) => !!input.prop('checked');
        options.setValue = (input, value) => input.prop('checked', value);

        await this.createInput(options);
    }

    /**
     * Creates a boolean input. Additional options: 
     * {
     *     range: {
     *          min,
     *          max,
     *          step
     *     }
     * }
     */
    async createNumericInput(options) {
        options.type = 'number';

        await this.createInput(options);
    }

    /**
     * Creates a text input.
     */
    async createTextInput(options) {
        options.type = 'text';

        await this.createInput(options);
    }

    /**
     * Creates a color input.
     */
    async createColorInput(options) {
        options.type = 'color';

        await this.createInput(options);
    }

    /**
     * Create a select input. Additional options:
     * {
     *     options: [
     *         {
     *             value:
     *             text
     *         }
     *     ]
     * }
     */
    async createSelectInput(options) {
        options.type = 'select';

        await this.createInput(options);
    }

    /**
     * Creates an input. Options:
     * 
     * {
     *     type,        "number", "select", "text", "color"
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
    async createInput(options) {
        const that = this;

        const input = this.#createInput(options);

        if (options.setValue) {
            options.setValue(input, options.value);
        } else {
            input.val(options.value);
        }

        async function onChange() {
            try {
                if (options.onChange) {
                    const value = options.getValue ? options.getValue(input) : input.val();
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
        }

        let messages = null;
        const inputCell = $('<td />').append(
            input
            .on('change', onChange)
            .prop('name', options.name)
        );

        if (options.type == "color") {
            inputCell.append(
                await this.#createAdditionalColorInputOptions(input, options.name, onChange)
            );
        }

        inputCell.append(
            options.additionalContent
        );

        inputCell.append(
            messages = $('<span class="parameter-check-messages" />')
        );

        if (!options.onChange) {
            input.prop('readonly', true);
        }

        if (options.range) {
            if (options.range.min) {
                input.prop('min', options.range.min);
            }
            if (options.range.max) {
                input.prop('max', options.range.max);
            }
            if (options.range.step) {
                input.prop('step', options.range.step);
            }
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

    #createInput(options) {
        return (options.type == 'select') 
            ? 
                $('<select />').append(
                    options.options.map((entry) => {
                        if (typeof entry == "object") {   
                            return $('<option />')
                                .prop('value', entry.value)
                                .text(entry.text ? entry.text : entry.value)
                        }
                        return $('<option />')
                            .prop('value', entry)
                            .text(entry) 
                    })
                )
            : 
                $('<input />')
                .prop('type', (options.type == "color") ? "text" : options.type)
    }

    /**
     * Additional stuff for color inputs
     */
    async #createAdditionalColorInputOptions(input, paramName, onChange) {
        if (!this.parser) return null;

        let colorInput = null;
        const that = this;

        async function updateColorInput() {
            const color = await that.parser.resolveColor(input.val());
            if (color) {
                colorInput.val(Tools.rgbToHex(color))
            }
        }

        const ret = [
            $('<select class="parameter-option parameter-color-select" />').append(
                (await this.parser.getAvailableColors())
                .concat([{
                    name: "Select color..."
                }])
                .map((item) => 
                    $('<option value="' + item.name + '" />')
                    .text(item.name)
                )
            )
            .on('change', async function() {
                const color = $(this).val();
                if (color == "Select color...") return;

                that.setParameter(paramName, color);
                //await that.setArgument(paramName, color);

                $(this).val("Select color...")

                await updateColorInput();

                await onChange();
            })
            .val("Select color..."),

            colorInput = $('<input type="color" class="parameter-option" />')
            .on('change', async function() {
                const rgb = Tools.hexToRgb($(this).val());
                const value = "(" + rgb[0] + ", " + rgb[1] + ", " + rgb[2] + ")";

                that.setParameter(paramName, value);
                //await that.setArgument(paramName, "(" + rgb[0] + ", " + rgb[1] + ", " + rgb[2] + ")");

                await onChange();
            })
        ];

        input.on('change', updateColorInput)
        await updateColorInput();

        return ret;
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