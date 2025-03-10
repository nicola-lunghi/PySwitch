/**
 * Metadata for functions
 */
class FunctionMeta {

    data = null;                   // Function metadata
    functionDefinition = null;     // Function descriptor
    client = null;

    constructor(parser, client, meta, functionDefinition) {
        this.client = client;
        this.data = meta || {};
        this.functionDefinition = functionDefinition;
    }   

    getCategory() {
        return this.data.category ? this.data.category : "none";
    }

    /**
     * Returns the display name for specific actions. If an action call proxy is passed, the 
     * argument values can be used to show more specific names.
     */
    getDisplayName(actionCallProxy = null) {
        return ((this.client.id != "local") ? (this.client.getDisplayName() + ": ") : "") + this.getShortDisplayName(actionCallProxy);
    }

    /**
     * Returns the display name for specific actions. If an action call proxy is passed, the 
     * argument values can be used to show more specific names.
     */
    getShortDisplayName(actionCallProxy = null) {
        switch (this.functionDefinition.name) {
            case "PagerAction": return "Pager";
            case "AnalogAction": return this.#getDisplayNameAnalogAction(actionCallProxy);
            case "EncoderAction": return this.#getDisplayNameEncoderAction(actionCallProxy);
        }
        return this.underscoreToDisplayName(this.functionDefinition.name);
    }

    /**
     * Converts underscore names to more readable ones
     */
     underscoreToDisplayName(str) {
        const splt = str.split("_");
        return splt.map((token) => token.charAt(0).toUpperCase() + token.substring(1).toLowerCase()).join(" ");
    }

    /**
     * Special implementation for AnalogAction
     */
    #getDisplayNameAnalogAction(actionCallProxy = null) {
        if (!actionCallProxy) return "AnalogAction";
        
        const mapping = this.getArgument(actionCallProxy, "mapping");

        if (!(mapping == null || mapping.value == "None")) {
            return this.underscoreToDisplayName(
                mapping.value
                .replace("MAPPING_", "")
                .replace("KemperMappings.", "")
                .replace(/\((.+?)*\)/g, "")
            );
        }

        return "AnalogAction";
    }   

    /**
     * Special implementation for EncoderAction
     */
    #getDisplayNameEncoderAction(actionCallProxy = null) {
        if (!actionCallProxy) return "EncoderAction";
        
        const mapping = this.getArgument(actionCallProxy, "mapping");

        if (!(mapping == null || mapping.value == "None")) {
            return this.underscoreToDisplayName(
                mapping.value
                .replace("MAPPING_", "")
                .replace("KemperMappings.", "")
                .replace(/\((.+?)*\)/g, "")
            );
        }

        return "EncoderAction";
    }

    /**
     * Gets the name of a argument in the given definition
     */
    getArgument(actionCallProxy = null, name) {
        if (!actionCallProxy) return null;
        
        const args = JSON.parse(actionCallProxy.arguments());

        for (const arg of args) {
            if (arg.name == name) return arg;
        }
        return null;
    }
}