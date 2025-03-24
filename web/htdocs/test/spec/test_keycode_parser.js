describe('Parser for available HID keycodes', function() {
    
    const tests = new KeycodeParserTests();

    beforeEach(async function() {
        jasmine.DEFAULT_TIMEOUT_INTERVAL = 20000;
    });

    it('Available keycodes', async function() {
        await tests.getAvailableKeycodes();
    });
});

