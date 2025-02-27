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
        return this.client.getDisplayName() + ": " + this.getShortDisplayName(actionCallProxy);
    }

    /**
     * Returns the display name for specific actions. If an action call proxy is passed, the 
     * argument values can be used to show more specific names.
     */
    getShortDisplayName(actionCallProxy = null) {
        return this.underscoreToDisplayName(this.functionDefinition.name);
    }

    /**
     * Converts underscore names to more readable ones
     */
     underscoreToDisplayName(str) {
        const splt = str.split("_");
        return splt.map((token) => token.charAt(0).toUpperCase() + token.substring(1).toLowerCase()).join(" ");
    }
}