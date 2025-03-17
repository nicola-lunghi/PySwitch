describe('Display Parser', function() {
    
    const tests = new DisplayParserTests();

    beforeEach(async function() {
        jasmine.DEFAULT_TIMEOUT_INTERVAL = 20000;
    });

    it('Get displays', async function() {
        await tests.getDisplaysDefault();
    });
});

