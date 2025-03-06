/**
 * Implements the parameter editor
 */
class ActionProperties {
    
    #actionDefinition = null;
    #inputs = null;
    #oldProperties = null;
    #advancedRows = null;
    #parser = null;
    #messages = null;

    constructor(parser, actionDefinition, oldProperties = null, messages = []) {
        this.#parser = parser;
        this.#actionDefinition = actionDefinition;
        this.#oldProperties = oldProperties;
        this.#messages = messages;
    }

    /**
     * Generate the DOM for the properties panel
     */
    async get() {
        this.#advancedRows = [];
        this.#inputs = new Map();

        let holdInput = null;

        /**
         * Take over old values from the old props object, if different from the default
         */
        function takeOverValues(input, param) {
            if (!that.#oldProperties) return;
                
            const oldParam = that.#oldProperties.getParameterDefinition(param.name);
            const oldValue = that.#oldProperties.getParameterValue(param.name);
            
            if (oldValue !== null && oldValue != oldParam.meta.getDefaultValue()) {
                that.#setInputValue(input, param, oldValue);
            }
        }

        const that = this;
        const parameters = await Promise.all(
            this.#actionDefinition.parameters
            .sort(function(a, b) {
                return (a.meta.data.advanced ? 1 : 0) + (b.meta.data.advanced ? -1 : 0);
            })
            .map(
                async (param) => {
                    const input = await this.#createInput(param);

                    that.#inputs.set(param, input);

                    // Take over old values from the old props object, if different from the default
                    takeOverValues(input, param);

                    // Get messages for the parameter
                    const messages = that.#messages.filter((item) => item.parameter == param.name)

                    // Build DOM for row
                    const row = $('<tr class="selectable" />').append(
                        // Parameter Name
                        $('<td />').append(
                            $('<span />').text(param.name)
                        ),

                        // Input
                        $('<td />')
                        .addClass(messages.length ? "has-messages" : null)
                        .append(
                            input                            
                        ),

                        // Comment
                        $('<td />').append(
                            await this.#getParameterComment(param)
                        )
                    );

                    if (!messages.length) {
                        // No messages: Hide if advanced
                        if (param.meta.data.advanced) {
                            that.#advancedRows.push({
                                row: row,
                                parameterName: param.name
                            });
                            row.hide();
                        }

                        return row;

                    } else {
                        // Messages: Also return additional rows. The result array (parameters) will be flattened later.
                        return [
                            // Main input row
                            row,

                            // Message rows
                            ...messages.map((item) => {
                                return $('<tr class="param-messages" />').append(
                                    $('<td />'),
    
                                    $('<td colspan="2" />').append(
                                        item.message
                                    )
                                )
                            })                            
                        ]
                    }
                }
            )
        );
        
        let tbody = null;

        const ret = $('<div class="action-properties" />').append(
            // Comment
            $('<div class="action-header" />')
            .text(this.#actionDefinition.meta.getDisplayName()),
            
            $('<div class="action-comment" />')
            .html(this.#getActionComment()),

            // Parameters
            $('<div class="action-header" />')
            .text("Parameters:"),
            
            $('<div class="action-parameters" />').append(
                $('<table />').append(
                    tbody = $('<tbody />').append(

                        // Hold option
                        (this.#actionDefinition.meta.data.target != "AdafruitSwitch") ? null :
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
                        parameters.flat()
                    )
                )
            )
        );

        // Advanced parameters: Show all button
        if (this.#advancedRows.length > 0) {
            let advRow = null;
            tbody.append(
                advRow = $('<tr />').append(
                    $('<td colspan="3" />').append(
                        $('<span class="show-advanced" />')
                        .text("Show all...")
                        .on('click', async function() {
                            for (const row of that.#advancedRows) {
                                row.row.show();
                            }

                            advRow.hide();
                        })
                    )
                )
            )
        }

        // Hold input
        if (this.#actionDefinition.meta.data.target == "AdafruitSwitch") {
            this.#inputs.set("hold", holdInput);
            if (this.#oldProperties) {
                this.setHold(this.#oldProperties.hold());            
            }
        }

        return ret;
    }

    /**
     * Returns an action definition which can be added to the Configuration.
     */
    createActionDefinition() {
        const that = this;

        return {
            name: this.#actionDefinition.name,
            arguments: this.#actionDefinition.parameters
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
        if (this.#actionDefinition.meta.data.target == "AdafruitSwitch") {
            return !!this.#inputs.get("hold").prop('checked');
        }
        return false;
    }

    /**
     * Sets the input values to the passed arguments list's values
     */
    setArguments(args) {
        const that = this;

        for (const arg of args) {
            // Get parameter definition first
            const param = this.getParameterDefinition(arg.name);
            const input = that.#inputs.get(param);
            if (!input) throw new Error("No input for param " + param.name + " found");

            this.#setInputValue(input, param, arg.value);

            // If not default value, show the row
            const defaultValue = param.meta.getDefaultValue()
            if (defaultValue != arg.value) {
                this.#showParameter(arg.name)
            }
        }
    }

    /**
     * Shows an advanced parameter
     */
    #showParameter(name) {
        for (const row of this.#advancedRows) {
            if (row.parameterName == name) {
                row.row.show();
            }
        }
    }

    /**
     * Sets the hold input
     */
    setHold(hold) {
        if (this.#actionDefinition.meta.data.target != "AdafruitSwitch") {
            return;
        }
        this.#inputs.get("hold").prop('checked', !!hold)
    }

    /**
     * Searches a parameter mode by name
     */
    getParameterDefinition(name) {
        for (const param of this.#actionDefinition.parameters) {
            if (param.name == name) return param;
        }
        return null;
    }

    /**
     * Determine the comment for the action
     */
    #getActionComment() {
        if (!this.#actionDefinition.comment) return "No information available";
        let comment = "" + this.#actionDefinition.comment;

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
                return this.#getNumberInput(param)

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
        .val(param.meta.getDefaultValue())
    }

    /**
     * Returns a parameter value by name
     */
    getParameterValue(name) {
        const param = this.getParameterDefinition(name);
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