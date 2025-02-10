class BankTests {

    #runner = null;

    constructor(runner) {
        this.#runner = runner;
    }

    async testBankUp(switchDef, labelTestCoordinates = null) {
        this.#runner.client.setRigId(0);
        await this.#runner.tick();
        
        expect(this.#runner.client.getRigId()).toBe(0);
        expect(this.#runner.getSwitchColor(switchDef)).toEqual([0, 0, 5]);
        if (labelTestCoordinates) expect(this.#runner.getDisplayColorAt(labelTestCoordinates)).toEqual([0, 0, 51]);

        await this.#runner.simulateSwitchPress(switchDef);

        expect(this.#runner.client.getRigId()).toBe(5);
        expect(this.#runner.getSwitchColor(switchDef)).toEqual([5, 5, 0]);
        if (labelTestCoordinates) expect(this.#runner.getDisplayColorAt(labelTestCoordinates)).toEqual([51, 51, 0]);
        
        await this.#runner.simulateSwitchPress(switchDef);
        
        expect(this.#runner.client.getRigId()).toBe(10);
        expect(this.#runner.getSwitchColor(switchDef)).toEqual([5, 0, 0]);
        if (labelTestCoordinates) expect(this.#runner.getDisplayColorAt(labelTestCoordinates)).toEqual([51, 0, 0]);
        
        await this.#runner.simulateSwitchPress(switchDef);

        expect(this.#runner.client.getRigId()).toBe(15);
        expect(this.#runner.getSwitchColor(switchDef)).toEqual([2, 5, 2]);
        if (labelTestCoordinates) expect(this.#runner.getDisplayColorAt(labelTestCoordinates)).toEqual([20, 51, 20]);
        
        await this.#runner.simulateSwitchPress(switchDef);

        expect(this.#runner.client.getRigId()).toBe(20);
        expect(this.#runner.getSwitchColor(switchDef)).toEqual([3, 0, 2]);
        if (labelTestCoordinates) expect(this.#runner.getDisplayColorAt(labelTestCoordinates)).toEqual([36, 0, 24]);
        
        await this.#runner.simulateSwitchPress(switchDef);

        expect(this.#runner.client.getRigId()).toBe(25); 
        expect(this.#runner.getSwitchColor(switchDef)).toEqual([0, 0, 5]);   
        if (labelTestCoordinates) expect(this.#runner.getDisplayColorAt(labelTestCoordinates)).toEqual([0, 0, 51]);

        // Overflow
        this.#runner.client.setRigId(125 * 5 - 1);
        await this.#runner.tick();

        expect(this.#runner.client.getRigId()).toBe(125 * 5 - 1);  
        expect(this.#runner.getSwitchColor(switchDef)).toEqual([3, 0, 2]);
        if (labelTestCoordinates) expect(this.#runner.getDisplayColorAt(labelTestCoordinates)).toEqual([36, 0, 24]);

        await this.#runner.simulateSwitchPress(switchDef);

        expect(this.#runner.client.getRigId()).toBe(4);  
        expect(this.#runner.getSwitchColor(switchDef)).toEqual([0, 0, 5]);  
        if (labelTestCoordinates) expect(this.#runner.getDisplayColorAt(labelTestCoordinates)).toEqual([0, 0, 51]);
    }
    
    async testBankDown(switchDef, labelTestCoordinates) {
        this.#runner.client.setRigId(23);
        await this.#runner.tick();

        expect(this.#runner.client.getRigId()).toBe(23);
        expect(this.#runner.getSwitchColor(switchDef)).toEqual([3, 0, 2]);
        if (labelTestCoordinates) expect(this.#runner.getDisplayColorAt(labelTestCoordinates)).toEqual([36, 0, 24]);

        await this.#runner.simulateSwitchPress(switchDef);

        expect(this.#runner.client.getRigId()).toBe(18);
        expect(this.#runner.getSwitchColor(switchDef)).toEqual([2, 5, 2]);
        if (labelTestCoordinates) expect(this.#runner.getDisplayColorAt(labelTestCoordinates)).toEqual([20, 51, 20]);
        
        await this.#runner.simulateSwitchPress(switchDef);

        expect(this.#runner.client.getRigId()).toBe(13);
        expect(this.#runner.getSwitchColor(switchDef)).toEqual([5, 0, 0]);
        if (labelTestCoordinates) expect(this.#runner.getDisplayColorAt(labelTestCoordinates)).toEqual([51, 0, 0]);
        
        await this.#runner.simulateSwitchPress(switchDef);

        expect(this.#runner.client.getRigId()).toBe(8);
        expect(this.#runner.getSwitchColor(switchDef)).toEqual([5, 5, 0]);
        if (labelTestCoordinates) expect(this.#runner.getDisplayColorAt(labelTestCoordinates)).toEqual([51, 51, 0]);
        
        await this.#runner.simulateSwitchPress(switchDef);

        expect(this.#runner.client.getRigId()).toBe(3);
        expect(this.#runner.getSwitchColor(switchDef)).toEqual([0, 0, 5]);
        if (labelTestCoordinates) expect(this.#runner.getDisplayColorAt(labelTestCoordinates)).toEqual([0, 0, 51]);
        
        await this.#runner.simulateSwitchPress(switchDef);
        
        expect(this.#runner.client.getRigId()).toBe(125 * 5 - 2);
        expect(this.#runner.getSwitchColor(switchDef)).toEqual([3, 0, 2]);
        if (labelTestCoordinates) expect(this.#runner.getDisplayColorAt(labelTestCoordinates)).toEqual([36, 0, 24]);
    }
}