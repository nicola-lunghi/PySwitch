/**
 * Kemper specific implementations for the parser
 */
class KemperParser extends Parser {

    /**
     * Returns a ClientDetector instance for the configuration
     */
    async getClientDetector() {
        return new KemperClientDetector();        
    }

    /**
     * Must return a virtual client
     */
    async getVirtualClient(config = {}) {
        return new VirtualKemperClient(
            {
                ...{
                    productType: 2,               // KPP
                    simulateMorphBug: true        // Simulate the morph button bug
                },
                ...config
            }
        );
    }

    /**
     * Can resolve tokens related to value ranges etc. in meta.json
     */
    async resolveValueToken(value) {
        switch(value) {
            case "NUM_BANKS": return 125;
            case "NUM_RIGS_PER_BANK": return 5;
        }

        return value;        
    }

    /**
     * Returns a sort string for the passed action definition
     */
    getActionSortString(action) {
        if (action.name == "BINARY_SWITCH") {
            return "ZZZZZ";
        }

        const category = action.meta.getCategory();
        
        switch (category) {
            case "rig": return "a" + action.meta.getDisplayName();
            case "bank": return "b" + action.meta.getDisplayName();
            case "effects": return "e";
            case "tuner": return "f";
            case "none": return "m";
            case "looper": return "w";
        }        
        return category;
    }

    createFunctionMeta(meta, funcDef) {
        return new KemperFunctionMeta(meta, funcDef);
    }
}