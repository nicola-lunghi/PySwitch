/**
 * Example test script, will be executed by a Jasmine test spec. See test/
 */
(async function(mappings, runner) {
    // Bank up/down
    const bankTests = new BankTests(runner);
    await bankTests.testBankUp(mappings.SWITCH_2, [238, 1]);
    await bankTests.testBankDown(mappings.SWITCH_B, [238, 238]);

    // Rig up/down
    const rigTests = new RigTests(runner);
    await rigTests.testRigUp(mappings.SWITCH_1);
    await rigTests.testRigDown(mappings.SWITCH_A);
})