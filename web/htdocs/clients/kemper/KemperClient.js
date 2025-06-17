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

    /**
     * If the client has callbacks implementations in __init__.py, this can return the class names for them.
     */
    getInitCallbacks() {
        return [
            'KemperRigNameCallback'
        ];
    }

    /**
     * Must return the Display Element which is the display root.
     */
    getSplashesRootElement(splashes) {
        switch(splashes.name) {
            case "TunerDisplayCallback":
                const splashDefault = Tools.getArgument(splashes, "splash_default");
                if (!splashDefault) throw new Error("No splash_default parameter found for TunerDisplayCallback");

                return splashDefault.value;
        }
        return splashes;
    }

    /**
     * Replaces the root splash element in the passed splashes object and returns if successful
     */
    setSplashesRootElement(splashes, rootElement) {
        switch(splashes.name) {
            case "TunerDisplayCallback":
                const splashDefault = Tools.getArgument(splashes, "splash_default");
                if (!splashDefault) throw new Error("No splash_default parameter found for TunerDisplayCallback");

                splashDefault.value = rootElement;
                return true;
        }
        return false;
    }

    /**
     * Returns optional global display parameters for the client as a ParameterList instance
     */
    getDisplayParameterList(editor) {
        return new KemperDisplayParameterList(editor);
    }
}