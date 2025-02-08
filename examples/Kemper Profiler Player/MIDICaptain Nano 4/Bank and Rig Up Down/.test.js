/**
 * Example test script, will be executed by a Jasmine test spec. See test/
 */
async function(mappings, runner) {
    expect(runner.client.getRigId()).toBe(0);

    // Push button 1
    await runner.simulateSwitchPress(mappings.SWITCH_1);
    expect(runner.client.getRigId()).toBe(1);
    
    await runner.simulateSwitchPress(mappings.SWITCH_1);
    expect(runner.client.getRigId()).toBe(2);
    
    await runner.simulateSwitchPress(mappings.SWITCH_1);
    expect(runner.client.getRigId()).toBe(3);
    
    await runner.simulateSwitchPress(mappings.SWITCH_1);
    expect(runner.client.getRigId()).toBe(4);
    
    await runner.simulateSwitchPress(mappings.SWITCH_1);
    expect(runner.client.getRigId()).toBe(4);    

    // Push button A
    await runner.simulateSwitchPress(mappings.SWITCH_A);
    expect(runner.client.getRigId()).toBe(3);

    await runner.simulateSwitchPress(mappings.SWITCH_A);
    expect(runner.client.getRigId()).toBe(2);

    await runner.simulateSwitchPress(mappings.SWITCH_A);
    expect(runner.client.getRigId()).toBe(1);

    await runner.simulateSwitchPress(mappings.SWITCH_A);
    expect(runner.client.getRigId()).toBe(0);

    await runner.simulateSwitchPress(mappings.SWITCH_A);
    expect(runner.client.getRigId()).toBe(0);

    // Push button 2
    await runner.simulateSwitchPress(mappings.SWITCH_2);
    expect(runner.client.getRigId()).toBe(5);
    
    await runner.simulateSwitchPress(mappings.SWITCH_2);
    expect(runner.client.getRigId()).toBe(10);
    
    await runner.simulateSwitchPress(mappings.SWITCH_2);
    expect(runner.client.getRigId()).toBe(15);
    
    await runner.simulateSwitchPress(mappings.SWITCH_2);
    expect(runner.client.getRigId()).toBe(20);
    
    await runner.simulateSwitchPress(mappings.SWITCH_2);
    expect(runner.client.getRigId()).toBe(25);    

    // Push button B
    await runner.simulateSwitchPress(mappings.SWITCH_B);
    expect(runner.client.getRigId()).toBe(20);
    
    await runner.simulateSwitchPress(mappings.SWITCH_B);
    expect(runner.client.getRigId()).toBe(15);
    
    await runner.simulateSwitchPress(mappings.SWITCH_B);
    expect(runner.client.getRigId()).toBe(10);
    
    await runner.simulateSwitchPress(mappings.SWITCH_B);
    expect(runner.client.getRigId()).toBe(5);
    
    await runner.simulateSwitchPress(mappings.SWITCH_B);
    expect(runner.client.getRigId()).toBe(0);

    await runner.simulateSwitchPress(mappings.SWITCH_B);
    expect(runner.client.getRigId()).toBe(0);

    // TODO Tuner test for all examples
}