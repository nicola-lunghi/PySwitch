class ExampleTestRunner {

    pyswitch = null;
    client = null;
    
    #examplesPath = "../examples";         // Path to the examples folder

    constructor() {
        this.pyswitch = new PySwitchRunner(
            {
                domNamespace: "pyswitch",
                updateIntervalMillis: 10
            }, 
            "test-pyswitch-example"
        );
    }

    /**
     * Process the tests. This loads a TOC of all tests and executes one after another, 
     * with behavioural mocks testing the functionality.
     */
    async process() {
        // Init pyodide
        await this.pyswitch.init("../");

        // Test all examples
        await this.#testExamples();
    }

    /**
     * Scans examples using the popup classes, and tests each one of the callable ones
     */
    async #testExamples() {
        const toc = await (new ExamplesProvider(this.#examplesPath + "/toc.php")).getToc();
        
        const that = this;
        async function crawl(entry) {
            if (entry.isCallable()) {
                await that.#testExample(entry);
                return;
            }

            for (const child of entry.children || []) {
                await crawl(child);
            }
        }

        await crawl(toc);
    }

    /**
     * Tests one BrowserEntry which contains an example
     */
    async #testExample(entry) {
        if (!entry.config.callPath) {
            console.warn("Skip example without callPath: ", entry);
            return;
        };

        const config = new WebConfiguration(this.#examplesPath + entry.config.callPath);
        
        // Create a temporary container element for pyswitch
        const el = $('<div id="test-pyswitch-example" />');
        $('body').append(el);

        // Set up virtual client
        this.client = await VirtualClient.getInstance(config);
        if (!this.client) {
            throw new Error(config.name + " does not support a virtual client device");
        }

        // Set client as MIDI wrapper to connect it to PySwitch
        this.pyswitch.setMidiWrapper(this.client);

        // Run without ticking at first
        await this.pyswitch.run(await config.get(), true);

        // Do some initial ticks
        let i = 0;
        while(i++ < 5) {
            await this.tick();
        }

        // Check if the bidirectional protocol is connecting
        await this.#initBidirectionalState();

        // Check if there is a test script: Tests must also have a mappings file, providing the mapping 
        // of the device inputs, in the parent folder.
        let testScript = null;
        let testSetup = null;
        
        try {
            testSetup = await Tools.fetch(this.#examplesPath + entry.config.callPath + "/../.test-mappings.js");
            testScript = await Tools.fetch(this.#examplesPath + entry.config.callPath + "/.test.js");            

        } catch (e) {
            // No test script
        }

        // Run the dedicated test if any has been found
        if (testSetup && testScript) {
            await this.#runExampleTest(testSetup, testScript);
        }        
        
        // Remove the test element from the body again
        el.remove();
    }

    /**
     * Checks that the bidirectional state is up and running
     */
    async #initBidirectionalState() {
        // Let the device connect with the virtual client first


        // TODO
    }

    /**
     * Performs each example's test case (eval)
     */
    async #runExampleTest(testSetup, testScript) {
        // Get mappings first
        const mappings = eval("(" + testSetup + ")");
        
        // Get the testing function and run it
        const test = eval("(" + testScript + ")");
        await test(mappings, this);
    }

    // Functions to be used by the test scripts ///////////////////////////////////////////////

    /**
     * Execute one tick
     */
    async tick() {
        await this.pyswitch.tick();
        await this.client.update();
    }

    /**
     * Simulates that a switch is pushed and released again, with ticks in between.
     */
    async simulateSwitchPress(id) {
        this.setSwitch(id, true);
        await this.tick();

        this.setSwitch(id, false);
        await this.tick();
    }

    /**
     * Sets a switches state
     */
    setSwitch(id, pushed) {
        const switchElement = this.#getSwitchElement(id);
        switchElement[0].dataset.pushed = pushed ? "true" : null;
    }

    /**
     * Gets a switch state
     */
    switchPushed(id) {
        const switchElement = this.#getSwitchElement(id);
        return switchElement[0].dataset.pushed == "true";
    }

    /**
     * Returns the switch element for a switch ID as defined in the mappings.
     */
    #getSwitchElement(id) {
        const switchElement = $("#pyswitch-switch-" + id);
        if (switchElement.attr('id') != "pyswitch-switch-" + id) throw new Error("Switch " + id + " not found");
        return switchElement;
    }
}