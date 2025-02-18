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
}