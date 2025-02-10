class RigTests {

    #runner = null;

    constructor(runner) {
        this.#runner = runner;
    }

    async testRigUp(switchDef, keep_bank = true) {
        this.#runner.client.setRigId(0);
        expect(this.#runner.client.getRigId()).toBe(0);
        if (labelTestCoordinates) expect(this.#runner.getDisplayColorAt(labelTestCoordinates)).toEqual([0, 0, 51]);

        await this.#runner.simulateSwitchPress(switchDef);
        expect(this.#runner.client.getRigId()).toBe(1);
        if (labelTestCoordinates) expect(this.#runner.getDisplayColorAt(labelTestCoordinates)).toEqual([0, 0, 51]);
        
        await this.#runner.simulateSwitchPress(switchDef);
        expect(this.#runner.client.getRigId()).toBe(2);
        if (labelTestCoordinates) expect(this.#runner.getDisplayColorAt(labelTestCoordinates)).toEqual([0, 0, 51]);
        
        await this.#runner.simulateSwitchPress(switchDef);
        expect(this.#runner.client.getRigId()).toBe(3);
        if (labelTestCoordinates) expect(this.#runner.getDisplayColorAt(labelTestCoordinates)).toEqual([0, 0, 51]);
        
        await this.#runner.simulateSwitchPress(switchDef);
        expect(this.#runner.client.getRigId()).toBe(4);
        if (labelTestCoordinates) expect(this.#runner.getDisplayColorAt(labelTestCoordinates)).toEqual([0, 0, 51]);
        
        if (keep_bank) {
            await this.#runner.simulateSwitchPress(switchDef);
            expect(this.#runner.client.getRigId()).toBe(4);        
            if (labelTestCoordinates) expect(this.#runner.getDisplayColorAt(labelTestCoordinates)).toEqual([0, 0, 51]);
        } else {
            await this.#runner.simulateSwitchPress(switchDef);
            expect(this.#runner.client.getRigId()).toBe(5);    
            if (labelTestCoordinates) expect(this.#runner.getDisplayColorAt(labelTestCoordinates)).toEqual([51, 51, 0]);

            // Overflow
            this.#runner.client.setRigId(125 * 5 - 1);

            await this.#runner.simulateSwitchPress(switchDef);
            expect(this.#runner.client.getRigId()).toBe(0);    
            if (labelTestCoordinates) expect(this.#runner.getDisplayColorAt(labelTestCoordinates)).toEqual([0, 0, 51]);
        }
    }
    
    async testRigDown(switchDef, keep_bank = true) {
        this.#runner.client.setRigId(23);
        expect(this.#runner.client.getRigId()).toBe(23);

        await this.#runner.simulateSwitchPress(switchDef);
        expect(this.#runner.client.getRigId()).toBe(22);
        
        await this.#runner.simulateSwitchPress(switchDef);
        expect(this.#runner.client.getRigId()).toBe(21);
        
        await this.#runner.simulateSwitchPress(switchDef);
        expect(this.#runner.client.getRigId()).toBe(20);
        
        if (keep_bank) {
            await this.#runner.simulateSwitchPress(switchDef);
            expect(this.#runner.client.getRigId()).toBe(20);    
        } else {
            await this.#runner.simulateSwitchPress(switchDef);
            expect(this.#runner.client.getRigId()).toBe(19);
            
            // Overflow
            this.#runner.client.setRigId(0);
    
            await this.#runner.simulateSwitchPress(switchDef);
            expect(this.#runner.client.getRigId()).toBe(125 * 5 - 1);    
        }
    }
}