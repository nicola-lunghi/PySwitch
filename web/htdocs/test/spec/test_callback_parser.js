describe('Parser for available callbacks', function() {
    
    const tests = new CallbackParserTests();

    it('Available callbacks', async function() {
        await tests.getAvailableDisplayLabelCallbacks();
    });
});

