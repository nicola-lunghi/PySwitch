describe('Parser for available mappings', function() {
    
    const tests = new MappingParserTests();

    beforeEach(async function() {
        jasmine.DEFAULT_TIMEOUT_INTERVAL = 20000;
    });

    it('Get available mappings', async function() {
        // console.error("Mapping parser tests are deactivated!");
        // return;  // TODO!

        await tests.getAvailableMappings();
    });

    it('Metadata', async function() {
        // console.error("Mapping parser tests are deactivated!");
        // return;  // TODO!

        await tests.getAvailableMappingsMeta();
    });
});

