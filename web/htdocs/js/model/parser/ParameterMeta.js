/**
 * Parameter metadata
 */
class ParameterMeta {

    client = null;
    data = null;          // Parameter metadata
    parameter = null;     // Parameter descriptor
    parser = null;
    #range = null;

    constructor(parser, client, meta, parameter) {
        this.client = client;
        this.data = meta || {};
        this.parameter = parameter;
        this.parser = parser;

        if (!this.parser) throw new Error("No parser passed")

        if (this.data.range) {
            this.#range = new ParameterRange(this);
        }
    }   

    /**
     * Returns a ParameterRange object if a range exists
     */
    range() {
        return this.#range;
    }

    /**
     * Tries to derive the parameter type from its default value. Returns null if not successful.
     */
    type() {
        if (this.data.type) return this.data.type;;

        const defaultValue = this.getDefaultValue();
        switch (defaultValue) {
            case "False": return "bool";
            case "True": return "bool";            
        }

        if (parseInt(defaultValue)) return "int";

        return null;
    }

    /**
     * If possible, returns a list of values, null if not possible.
     */
    async getValues() {
        if (this.parameter.name == "display" || this.parameter.name == "morph_display") {
            function formatUsages(usages) {
                if (usages.length == 0) return "";
                const usagemap = usages.map((item) => item.input.displayName());
                return " (" + usagemap.join(", ") + ")";
            }
    
            return Promise.all(
                (await this.parser.getAvailableDisplays())
                    .map(async (item) => {
                        return {
                            name: item + formatUsages(await this.parser.checks.getDisplayUsages(item)),
                            value: item
                        };
                    })
                    .concat([{
                        name: "None",
                        value: "None"
                    }])
                )
        }

        if (this.parameter.name == "mapping") {
            return this.#generateMappingOptions();
        }
   
        if (this.#range) return this.#range.getValues();

        return this.data.values || null;
    }

    /**
     * Generates the mapping list for input
     */
    async #generateMappingOptions() {
        async function getMappingVariants(mapping) {
            if (mapping.parameters.length == 0) {
                return [
                    {
                        name: mapping.name + "()",
                        value: mapping.name + "()"
                    }
                ]
            }

            // We only resolve the first parameter here (mappings never have more)
            const param = mapping.parameters[0];

            function addValues(values) {
                for(const value of values) {
                    const argStr = (mapping.parameters.length > 1) ? (param.name + " = ") : "";

                    ret.push({
                        name: mapping.name + "(" + argStr + value.value + ")",
                        value: mapping.name + "(" + argStr + value.value + ")"
                    });
                }
            }

            const ret = [];
            if (param.meta && param.meta.range()) {
                const values = await param.meta.range().getValues();
                addValues(values);

            } else if (param.meta && param.meta.data.values) {
                addValues(param.meta.data.values);
                
            } else {
                throw new Error("No parameter values for parameter " + param.name + " of mapping " + mapping.name + " found in meta.json")
            }
            return ret;
        }

        const clients = await this.parser.getAvailableMappings();

        let ret = [];
        for (const client of clients) {
            for(const mapping of client.mappings) {
                ret = ret.concat(await getMappingVariants(mapping))
            }
        }
        return ret;
    }

    /**
     * Determines the default value for the parameter
     */
    getDefaultValue() {
        // If we have a parameter default, use it
        if (this.parameter.default) {
            return this.parameter.default;
        }

        // If we have a default defined in the metadata, use it
        if (this.data.default) {
            return this.data.default;
        }

        const that = this;

        function getNumberDefault() {
            if (that.data.range && that.data.range.min) {
                return "" + that.data.range.min;
            }
            return "0";
        }

        function getSelectDefault() {
            if (!that.data.values) return ""; //throw new Error("No values for select type: " + that.parameter.name);

            return "" + that.data.values[0].value;
        }

        // If we have a type definition, derive the default from this
        if (this.data.type) {
            switch (this.data.type) {
                case "int": return getNumberDefault();
                case "float": return getNumberDefault();
                case "select": return getSelectDefault();
                case "select-page": return getSelectDefault();
                case "bool": return "False";
                case "color": return "(0, 0, 0)";
                default: throw new Error("Unknown parameter type: " + this.data.type);
            }
        }
        
        // Last fallback: None
        return "None";
    }

    /**
     * Input conversion (applied when entries are set by user input for example).
     */
    convertInput(value) {
        const that = this;
        
        function convertInputText(v) {
            // Specific values can be excluded from auto-quoting
            for (const ucv of that.data.unconvertedValues || []) {
                if (ucv == v) return v
            }

            return Tools.autoQuote(v);
        }

        // Input conversion for specific types
        switch (this.type()) {
            case "text": return convertInputText(value);
        }

        // No conversion
        return value;
    }
}