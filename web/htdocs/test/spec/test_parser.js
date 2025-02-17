describe('Parser', function() {
    
    const tests = new KemperParserTests();

    beforeEach(async function() {
        jasmine.DEFAULT_TIMEOUT_INTERVAL = 20000;
    });

    // it('TODO', async function() {
    //     await tests.process();
    // });

    it('Minimal call', async function() {
        await tests.minimal();
    });

    it('Get input actions for a port (default)', async function() {
        await tests.getInputActionsDefault();
    });

    it('Get input actions for a port (hold)', async function() {
        await tests.getInputActionsHold();
    });

    it('Remove actions', async function() {
        await tests.removeAction();
    });

    it('Remove actions (hold)', async function() {
        await tests.removeActionHold();
    });

    it('Append action', async function() {
        await tests.addActionNoIndex();
    });

    it('Add action at index', async function() {
        await tests.addActionWithIndex();
    });

    it('Append hold action', async function() {
        await tests.addActionHoldNoIndex();
    });
});

