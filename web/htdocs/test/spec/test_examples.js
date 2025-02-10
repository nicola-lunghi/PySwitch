describe('Examples', function() {
    
    beforeEach(function() {
        jasmine.DEFAULT_TIMEOUT_INTERVAL = 20000;
    });

    it('Examples (high level test)', async function() {
        await (new ExampleTestRunner().process());   
    });
});

