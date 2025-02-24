class ActionProperties {
    
    #parser = null;
    #model = null;

    constructor(parser, model) {
        this.#parser = parser;
        this.#model = model;
    }

    /**
     * Generate the DOM for the properties panel
     */
    async get() {
        return $('<div class="action-properties" />').append(
            // Comment
            $('<div class="action-header" />')
            .text("Description:"),
            
            $('<div class="action-comment" />')
            .html(this.#getActionComment()),

            // Parameters
            $('<div class="action-header" />')
            .text("Parameters:"),
            
            $('<div class="action-parameters" />').append(
                $('<table />').append(
                    $('<tbody />').append(
                        await Promise.all(
                            this.#model.parameters.map(
                                async (param) => {
                                    return $('<tr />').append(
                                        // Parameter Name
                                        $('<td />').append(
                                            $('<span />').text(param.name)
                                        ),
                
                                        // Input
                                        $('<td />').append(
                                            await this.#getInput(param)
                                        ),
                
                                        // Comment
                                        $('<td />').append(
                                            await this.#getParameterComment(param)
                                        )
                                    );
                                }
                            )
                        )
                    )
                )
            )
            
            // // Buttons
            // $('<div class="action-buttons" />').append(
            //     $('<div class="button" />')
            //     .text("Add")
            // )            
        )
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
        if (!param.comment) return "";
        return param.comment;
    }

    /**
     * Generates the DOM for one parameter
     */
    async #getInput(param) {
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
                if (param.meta.data.values) {
                    return $('<select />').append(
                        param.meta.data.values.map((option) => 
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
     * Create a numeric input (int)
     */
    async #getNumberInput(param) {
        const range = new ParameterRange(this.#parser, param.meta.data.range);

        // return $('<input type="number" />')
        //     .attr('min', await range.min())
        //     .attr('max', await range.max())
        //     .val(param.meta.getDefaultValue());

        const values = await Promise.all(await range.getValues());

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