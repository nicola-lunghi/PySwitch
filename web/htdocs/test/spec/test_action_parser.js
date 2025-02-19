describe('Parser for available actions', function() {
    
    const tests = new ActionParserTests();

    beforeEach(async function() {
        jasmine.DEFAULT_TIMEOUT_INTERVAL = 20000;
    });

    it('Available actions', async function() {
        // console.error("Action parser tests are deactivated!");
        // return;  // TODO!

        await tests.getAvailableActions();
    });

    it('Metadata', async function() {
        // console.error("Action parser tests are deactivated!");
        // return;  // TODO!

        await tests.getAvailableActionsMeta();
    });
});

