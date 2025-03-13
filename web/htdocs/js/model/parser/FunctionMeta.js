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
            case "PagerAction": return this.#getDisplayNamePager(actionCallProxy);
            case "PagerAction.proxy": return this.#getDisplayNamePagerProxy(actionCallProxy);
            case "AnalogAction": return this.#getDisplayNameAnalogAction(actionCallProxy);
            case "EncoderAction": return this.#getDisplayNameEncoderAction(actionCallProxy);
        }
        return this.underscoreToDisplayName(this.functionDefinition.name);
    }

    /**
     * Returns a sort string for the action definition
     */
    async getSortString() {
        if (this.functionDefinition.name.startsWith("PagerAction")) {
            return "ZZZZZZZZ" + this.functionDefinition.name;
        }

        return this.functionDefinition.name;
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
     * Special implementation for PagerAction
     */
    #getDisplayNamePager(actionCallProxy = null) {
        if (!actionCallProxy) return "Pager";
        
        const select_page = this.getArgument(actionCallProxy, "select_page");

        if (!(select_page == null || select_page.value == "None")) {
            return "Select " + actionCallProxy.assign + "|" + select_page.value;
        }

        return "Rotate " + actionCallProxy.assign;
    }   

    

    /**
     * Special implementation for PagerAction.proxy
     */
    #getDisplayNamePagerProxy(actionCallProxy = null) {
        if (!actionCallProxy) return "Select Page";
        
        const page_id = this.getArgument(actionCallProxy, "page_id");
        const pager = this.#extractPager(actionCallProxy.name);

        if (!(page_id == null || page_id.value == "None")) {
            return "Select " + pager + "|" + page_id.value;
        }

        return "Select Page";
    }   

    /**
     * Extracts the pager name from _pager.xxx
     */
    #extractPager(name) {
        const splt = name.split(".");
        if (!splt.length == 2) return null;

        return splt[0];
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