describe('Parser for available DisplayLabel callbacks', function() {
    
    const tests = new CallbackParserTests();

    it('Available callbacks', async function() {
        await tests.getAvailableDisplayLabelCallbacks();
    });
});

