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
        if (!actionDefinition) return str;
        return str;
        // for (const arg of actionDefinition.arguments) {

        // }
    }
}