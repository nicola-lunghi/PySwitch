/**
 * Example test script, will be executed by a Jasmine test spec. When you have the PySwitch emulator 
 * docker container running, you can run the tests calling http://localhost/test
 */
(async function(mappings, runner) {
    // Tuner display
    await (new KemperTunerTests(runner)).testTriggeredFromClient({
        switchDefinitions: [
            mappings.SWITCH_1,
            mappings.SWITCH_2,
            mappings.SWITCH_A,
            mappings.SWITCH_B
        ]
    });

    // Bank up/down
    const bankTests = new KemperBankTests(runner);
    await bankTests.testBankUp(mappings.SWITCH_2, { labelTestCoordinates: [238, 1] });
    await bankTests.testBankDown(mappings.SWITCH_B, { labelTestCoordinates: [238, 238] });

    // Rig up/down
    const rigTests = new KemperRigTests(runner);
    await rigTests.testRigUp(mappings.SWITCH_1, { keepBank: false, labelTestCoordinates: [1, 1] });
    await rigTests.testRigDown(mappings.SWITCH_A, { keepBank: false, labelTestCoordinates: [1, 238] });
})