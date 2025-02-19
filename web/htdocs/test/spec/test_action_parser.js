describe('Parser for available actions', function() {
    
    const tests = new ActionParserTests();

    beforeEach(async function() {
        jasmine.DEFAULT_TIMEOUT_INTERVAL = 20000;
    });

    it('Get available actions', async function() {
        // console.error("Action parser tests are deactivated!");
        // return;  // TODO!

        await tests.getAvailableActions();
    });
});

