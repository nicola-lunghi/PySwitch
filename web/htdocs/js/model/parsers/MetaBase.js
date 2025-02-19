class MetaBase {

    entity = null;

    constructor(entity) {
        this.entity = entity;
    }

    /**
     * Replaces all tokens for parameters
     */
    replaceParameterTokens(actionDefinition, str) {
        function getReplaceValue(param) {
            for (const def of (actionDefinition ? (actionDefinition.arguments || []) : [])) {
                if (def.name == param.name) {
                    return def.value;
                }
            }

            return param.meta.getDefaultValue();
        }

        function replaceToken(str, token, value) {
            return str.replace("{" + token + "}", "" + value);
        }

        for (const param of this.entity.parameters) {
            str = replaceToken(str, param.name, getReplaceValue(param))
        }

        return str;
    }

    /**
     * Gets the name of a argument in the given definition
     */
    getArgument(definition, name) {
        if (!definition) return null;
        
        for (const arg of definition.arguments) {
            if (arg.name == name) return arg;
        }
        return null;
    }
}