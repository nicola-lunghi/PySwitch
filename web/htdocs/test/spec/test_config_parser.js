describe('Configuration Parser', function() {
    
    const tests = new ConfigParserTests();

    beforeEach(async function() {
        jasmine.DEFAULT_TIMEOUT_INTERVAL = 20000;
    });

    it('Minimal call', async function() {
        await tests.minimal();
    });

    it('Get input actions for a port (default)', async function() {
        await tests.getInputActionsDefault();
    });

    it('Get input actions for a port (hold)', async function() {
        await tests.getInputActionsHold();
    });

    it('Replace actions', async function() {
        await tests.replaceActions();
    });

    it('Create new inputs', async function() {
        await tests.createNewInputs();
    });

    it('Auto-add imports (all actions)', async function() {
        await tests.addAllImports();
    });

    it('Auto-add imports (one action)', async function() {
        await tests.addOneImport();
    });

    it('Auto-add imports (display.py)', async function() {
        await tests.addDisplayImports();
    });

    it('Display name: Generic', async function() {
        await tests.displayNameGeneric();
    });

    it('Display name: RIG_SELECT', async function() {
        await tests.displayNameRigSelect();
    });

    it('Display name: RIG_SELECT (with rig_off)', async function() {
        await tests.displayNameRigSelectToggle();
    });

    it('Display name: Bank Select', async function() {
        await tests.displayNameBankSelect();
    });

    // it('Remove actions', async function() {
    //     await tests.removeAction();
    // });

    // it('Remove actions (hold)', async function() {
    //     await tests.removeActionHold();
    // });

    // it('Append action', async function() {
    //     await tests.addActionNoIndex();
    // });

    // it('Add action at index', async function() {
    //     await tests.addActionWithIndex();
    // });

    // it('Append hold action', async function() {
    //     await tests.addActionHoldNoIndex();
    // });
});

