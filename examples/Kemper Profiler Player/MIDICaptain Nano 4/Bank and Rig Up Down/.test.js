/**
 * Example test script, will be executed by a Jasmine test spec. See test/
 */
(async function(mappings, runner) {
    // Bank up/down
    const bankTests = new KemperBankTests(runner);
    await bankTests.testBankUp(mappings.SWITCH_2, { labelTestCoordinates: [238, 1] });
    await bankTests.testBankDown(mappings.SWITCH_B, { labelTestCoordinates: [238, 238] });

    // Rig up/down
    const rigTests = new KemperRigTests(runner);
    await rigTests.testRigUp(mappings.SWITCH_1, { keepBank: true, labelTestCoordinates: [1, 1] });
    await rigTests.testRigDown(mappings.SWITCH_A, { keepBank: true, labelTestCoordinates: [1, 238] });
})