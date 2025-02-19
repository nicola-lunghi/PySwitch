class ParameterMeta {

    #meta = null;         // Parameter metadata
    #parameter = null;    // Parameter descriptor

    constructor(meta, parameter) {
        this.#meta = meta;
        this.#parameter = parameter;
    }   

    toJSON() {
        return this.#meta || {}
    }

    /**
     * Determines the default value for the parameter
     */
    getDefaultValue() {
        // If we have a parameter default, use it
        if (this.#parameter.default) {
            return this.#parameter.default;
        }

        if (!this.#meta) {
            return "None";
        }

        // If we have a default defined in the metadata, use it
        if (this.#meta.default) {
            return this.#meta.default;
        }

        const that = this;

        function getNumberDefault() {
            if (that.#meta.range && that.#meta.range.min) {
                return "" + that.#meta.range.min;
            }
            return "0";
        }

        function getSelectDefault() {
            if (!that.#meta.values) throw new Error("No values for select type: " + that.parameter.name);

            return "" + that.#meta.values[0].value;
        }

        // If we have a type definition, derive the default from this
        if (this.#meta.type) {
            switch (this.#meta.type) {
                case "int": return getNumberDefault();
                case "float": return getNumberDefault();
                case "select": return getSelectDefault();
                case "bool": return "False";
                case "color": return "(0, 0, 0)";
                default: throw new Error("Unknown parameter type: " + this.#meta.type);
            }
        }
        
        // Last fallback: None
        return "None";
    }
}