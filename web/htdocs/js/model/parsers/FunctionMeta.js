class FunctionMeta {

    #meta = null;         // Function metadata
    #function = null;     // Function descriptor

    constructor(meta, func) {
        this.#meta = meta;
        this.#function = func;
    }   

    toJSON() {
        return this.#meta || {}
    }

    /**
     * Determines the default value for the parameter. Expects an action definition as used for the parser API.
     * If an actionDefinition with arguments is passed, these arguments are used to replace tokens.
     */
    getDisplayName(actionDefinition = null) {
        if (!this.#meta) {
            return this.#function.name;
        }

        if (this.#meta.displayName) {
            return this.#replaceParameterTokens(actionDefinition, this.#meta.displayName);
        }

        return this.#function.name;
    }

    /**
     * Replaces all tokens for parameters
     */
    #replaceParameterTokens(actionDefinition, str) {
        function getReplaceValue(param) {
            for (const def of (actionDefinition ? (actionDefinition.arguments || []) : [])) {
                if (def.name == param.name) {
                    return def.value;
                }
            }

            return param.meta.getDefaultValue();
        }

        for (const param of this.#function.parameters) {
            str = this.#replaceToken(str, param.name, getReplaceValue(param))
        }

        return str;
    }

    /**
     * Token replacement (basic)
     */
    #replaceToken(str, token, value) {
        return str.replace("{" + token + "}", "" + value);
    }
}