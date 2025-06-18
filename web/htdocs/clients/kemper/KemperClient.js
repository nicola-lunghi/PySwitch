/**
 * CLient implementations for Kemper devices
 */
class KemperClient extends Client {
    
    /**
     * Returns a display name for the client
     */
    getDisplayName() {
        return "Kemper";
    }
    
    /**
     * Factory for FunctionMeta instances
     */
    async createFunctionMeta(parser, meta, funcDef) {
        return new KemperFunctionMeta(parser, this, meta, funcDef);
    }

    /**
     * Factory for ParameterMeta instances
     */
    async createParameterMeta(parser, meta, paramDef) {
        return new KemperParameterMeta(parser, this, meta, paramDef);
    }

    /**
     * Returns a ClientDetector instance for the client, or none if not implemented
     */
    async getClientDetector() {
        return new KemperClientDetector();        
    }

    /**
     * Must return a virtual client
     */
    async getVirtualClient(options) {
        return new VirtualKemperClient(
            {
                ...{
                    productType: 2,               // KPP
                    simulateMorphBug: true        // Simulate the morph button bug                
                },
                ...options
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
     * If the client has action implementations in __init__.py, this can return the class name for them.
     */
    getInitMappingsClassName() {
        return "KemperMappings";
    }
}