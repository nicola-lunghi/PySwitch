/**
 * Implements the parameter editor
 */
class ActionProperties {
    
    #parser = null;
    #model = null;
    #inputs = null;
    #oldProperties = null;
    #advancedRows = null;

    constructor(parser, model, oldProperties = null) {
        this.#parser = parser;
        this.#model = model;
        this.#oldProperties = oldProperties;   
    }

    /**
     * Generate the DOM for the properties panel
     */
    async get() {
        this.#advancedRows = [];
        this.#inputs = new Map();

        let holdInput = null;

        const that = this;
        const parameters = await Promise.all(
            this.#model.parameters
            .map(
                async (param) => {
                    const input = await this.#createInput(param);

                    that.#inputs.set(param, input);

                    // Take over old values from the old props object, if different from the default
                    if (that.#oldProperties) {
                        const oldParam = that.#oldProperties.getParameterModel(param.name);
                        const oldValue = that.#oldProperties.getParameterValue(param.name);
                        
                        if (oldValue !== null && oldValue != oldParam.meta.getDefaultValue()) {
                            that.#setInputValue(input, param, oldValue);
                        }   
                    }

                    const row = $('<tr />').append(
                        // Parameter Name
                        $('<td />').append(
                            $('<span />').text(param.name)
                        ),

                        // Input
                        $('<td />').append(
                            input
                        ),

                        // Comment
                        $('<td />').append(
                            await this.#getParameterComment(param)
                        )
                    );

                    if (param.meta.data.advanced) {
                        that.#advancedRows.push(row);
                        row.hide();
                    }

                    return row;
                }
            )
        );

        let tbody = null;

        const ret = $('<div class="action-properties" />').append(
            // Comment
            $('<div class="action-header" />')
            .text(this.#model.meta.getDisplayName()),
            
            $('<div class="action-comment" />')
            .html(this.#getActionComment()),

            // Parameters
            $('<div class="action-header" />')
            .text("Parameters:"),
            
            $('<div class="action-parameters" />').append(
                $('<table />').append(
                    tbody = $('<tbody />').append(

                        // Hold option
                        $('<tr />').append(
                            $('<td />').append(
                                $('<span />').text("hold")
                            ),
    
                            // Input
                            $('<td />').append(
                                holdInput = $('<input type="checkbox" />')
                                .prop('checked', false)
                            ),
    
                            // Comment
                            $('<td />').text("")
                        ),

                        // Action parameters
                        parameters
                    )
                )
            )
        );

        if (this.#advancedRows.length > 0) {
            let advRow = null;
            tbody.append(
                advRow = $('<tr />').append(
                    $('<td colspan="3" />').append(
                        $('<span class="show-advanced" />')
                        .text("Show all...")
                        .on('click', async function() {
                            for (const row of that.#advancedRows) {
                                row.show();
                            }

                            advRow.hide();
                        })
                    )
                )
            )
        }

        this.#inputs.set("hold", holdInput);

        if (this.#oldProperties) {
            this.setHold(this.#oldProperties.hold());            
        }

        return ret;
    }

    /**
     * Returns an action definition which can be added to the config.
     */
    createActionDefinition() {
        const that = this;

        return {
            name: this.#model.name,
            arguments: this.#model.parameters
                .filter((param) => {
                    const input = that.#inputs.get(param);
                    if (!input) throw new Error("No input for param " + param.name + " found");
        
                    const value = that.#getInputValue(input, param);

                    return !param.hasOwnProperty("default") || (value != param.default);
                })
                .map((param) => {
                    const input = that.#inputs.get(param);
                    if (!input) throw new Error("No input for param " + param.name + " found");
        
                    return {
                        name: param.name,
                        value: that.#getInputValue(input, param)
                    };
                })
        }
    }

    /**
     * Returns if the user selected hold or not (JS bool, no python value)
     */
    hold() {
        return !!this.#inputs.get("hold").prop('checked')
    }

    /**
     * Sets the input values to the passed arguments list's values
     */
    setArguments(args) {
        const that = this;

        for (const arg of args) {
            // Get parameter definition first
            const param = this.getParameterModel(arg.name);
            const input = that.#inputs.get(param);
            if (!input) throw new Error("No input for param " + param.name + " found");

            this.#setInputValue(input, param, arg.value);
        }
    }

    /**
     * Sets the hold input
     */
    setHold(hold) {
        this.#inputs.get("hold").prop('checked', !!hold)
    }

    /**
     * Searches a parameter mode by name
     */
    getParameterModel(name) {
        for (const param of this.#model.parameters) {
            if (param.name == name) return param;
        }
        return null;
    }

    /**
     * Determine the comment for the action
     */
    #getActionComment() {
        if (!this.#model.comment) return "No information available";
        let comment = "" + this.#model.comment;

        if (comment.slice(-1) != ".") comment += ".";

        return comment;
    }

    /**
     * Determine parameter comment
     */
    #getParameterComment(param) {
        if (param.meta.data.comment) return param.meta.data.comment;
        if (!param.comment) return "";
        return param.comment;
    }

    /**
     * Generates the DOM for one parameter
     */
    async #createInput(param) {
        let type = param.meta.data.type;

        if (!type) {
            type = this.#deriveType(param);
        }

        switch(type) {
            case "bool":                
                return $('<input type="checkbox" />')
                .prop('checked', param.meta.getDefaultValue() == "True")

            case "int":                
                return this.#getNumberInput(param);

            case 'select':
                const values = await param.meta.getValues();
                if (values) {
                    return $('<select />').append(
                        values.map((option) => 
                            $('<option value="' + option.value + '" />')
                            .text(option.name)
                        )                        
                    )
                    .val(param.meta.getDefaultValue())
                }
                break;               
        }        

        return $('<input type="text" />')
        .val(param.meta.getDefaultValue());
    }

    /**
     * Returns a parameter value by name
     */
    getParameterValue(name) {
        const param = this.getParameterModel(name);
        if (!param) return null;

        const input = this.#inputs.get(param);
        if (!input) return null;

        return this.#getInputValue(input, param);        
    }

    /**
     * Converts the input values to action argument values
     */
    #getInputValue(input, param) {
        let type = param.meta.data.type;

        if (!type) {
            type = this.#deriveType(param);
        }

        switch(type) {
            case "bool": return input.prop('checked') ? "True" : "False";
        }        

        let value = input.val();
        if (value == "") value = param.meta.getDefaultValue();

        return value;        
    }

    /**
     * Sets the input value according to an argumen/parameter value
     */
    #setInputValue(input, param, value) {
        let type = param.meta.data.type;

        if (!type) {
            type = this.#deriveType(param);
        }

        switch(type) {
            case "bool": 
                input.prop('checked', value == "True");
                break;

            default:
                input.val(value);
        }      
    }

    /**
     * Create a numeric input (int)
     */
    async #getNumberInput(param) {
        const range = param.meta.range();
        if (!range) {
            return $('<input type="number" />')
                .val(param.meta.getDefaultValue());
        }

        const values = await param.meta.getValues();

        return $('<select />').append(
            values.map((option) => 
                $('<option value="' + option.value + '" />')
                .text(option.name)
            )
        ) 
    }

    /**
     * Tries to derive the parameter type from its default value. Returns null if not successful.
     */
    #deriveType(param) {
        const defaultValue = param.meta.getDefaultValue();
        switch (defaultValue) {
            case "False": return "bool";
            case "True": return "bool";            
        }

        if (parseInt(defaultValue)) return "int";

        return null;
    }
}