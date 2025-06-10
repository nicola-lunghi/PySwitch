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

        const options = this.#getRows();
        const headline = await this.getHeadline();

        return $('<span class="parameter-list-container" />').append(
            $('<div class="parameter-list" />').append(
                !headline ? null :
                $('<div class="parameter-comment" />')
                .html(headline),

                !options ? null :
                $('<div class="parameters" />').append(
                    $('<table />').append(
                        $('<tbody />').append(
                            options
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
        // Implement in child classes
    }
    
    ///////////////////////////////////////////////////////////////////////////////////////

    /**
     * Creates a boolean input
     */
    createBooleanInput(name, comment, value, onChange) {
        const that = this;

        let input = null;
        const inputCell = $('<td />').append(
            input = $('<input type="checkbox" />')
            .on('change', async function() {
                try {
                    await onChange(!!$(this).prop('checked'))
                
                } catch (e) {
                    that.controller.handle(e);
                }
            })
            .prop('checked', value)
        )

        this.#inputs.push({
            row: Tools.withComment(
                $('<tr />').append(                            
                    $('<td />').append(
                        $('<span />').text(name)
                    ),

                    inputCell
                ),
                comment
            ),
            input: input
        })
    }

    /**
     * Creates a numeric input
     */
    createNumericInput(name, comment, value, onChange) {
        const that = this;

        let input = null;
        const inputCell = $('<td />').append(
            input = $('<input type="number" />')
            .on('change', async function() {
                try {
                    await onChange($(this).val())
                
                } catch (e) {
                    that.controller.handle(e);
                }
            })
            .val(value)
        )

        this.#inputs.push({
            name: name,
            row: Tools.withComment(
                $('<tr />').append(                            
                    $('<td />').append(
                        $('<span />').text(name)
                    ),

                    inputCell
                ),
                comment
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