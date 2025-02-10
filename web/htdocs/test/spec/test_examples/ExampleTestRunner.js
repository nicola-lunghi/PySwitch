class ExampleTestRunner {

    pyswitch = null;
    client = null;
    
    #examplesPath = "../examples";               // Path to the examples folder
    #timeMillis = 0;                             // Current time in milliseconds for the simulations

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

        // Reset virtual simulation time
        this.#timeMillis = 0;

        // Set up virtual client
        const that = this;
        this.client = await VirtualClient.getInstance(config, {
            overrideTimeCallback: function() {
                return that.#timeMillis;
            }
        });
        if (!this.client) {
            throw new Error(config.name + " does not support a virtual client device");
        }

        // Set client as MIDI wrapper to connect it to PySwitch
        this.pyswitch.setMidiWrapper(this.client);

        // Override current time
        this.pyswitch.setTimeCallback(function() {
            return that.#timeMillis / 1000;
        });

        // Run without ticking at first
        await this.pyswitch.run(await config.get(), true);

        // Do some initial ticks to get the bidirectional protocol connected
        let i = 0;
        while(i++ < 100) {
            await this.tick();
        }

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
     * Performs each example's test case (eval)
     */
    async #runExampleTest(testSetup, testScript) {
        // Get mappings first
        const mappings = eval(testSetup);
        
        // Get the testing function and run it
        const test = eval(testScript);
        await test(mappings, this);
    }

    // Functions to be used by the test scripts ///////////////////////////////////////////////

    /**
     * Execute one tick for a given amount of milliseconds (default is one second).
     */
    async tick(stepMillis = 100) {
        this.#timeMillis += stepMillis;

        await this.pyswitch.tick();
        await this.client.update();
    }

    /**
     * Simulates that a switch is pushed and released again, with ticks in between.
     */
    async simulateSwitchPress(switchDef, holdTime = 100) {
        await this.tick();
        
        this.setSwitch(switchDef, true);
        await this.tick(holdTime);

        this.setSwitch(switchDef, false);
        await this.tick();
    }

    /**
     * Sets a switches state
     */
    setSwitch(switchDef, pushed) {
        const switchElement = this.#getSwitchElement(switchDef);
        switchElement[0].dataset.pushed = pushed ? "true" : null;
    }

    /**
     * Gets a switch state
     */
    switchPushed(switchDef) {
        const switchElement = this.#getSwitchElement(switchDef);
        return switchElement[0].dataset.pushed == "true";
    }    

    /**
     * Gets the color of a switch. If the switch has multiple colors, this 
     * will throw. Use getSwitchColors() instead for those.
     */
    getSwitchColor(switchDef) {
        const ledElements = this.#getLedElements(switchDef);

        let color = null;
        for(const ledElement of ledElements) {
            const rgb = JSON.parse(ledElement[0].dataset.color); //ledElement[0].style.backgroundColor.match(/\d+/g).map((item) => parseInt(item));
            
            if (color === null) {
                color = rgb;
            } else {
                if (!Tools.compareArrays(color, rgb)) throw new Error("Switch has multiple colors, but is expected to only have one");
            }            
        }

        return color;
    }

    /**
     * Returns the display color at the given pixel. position must be an array with [x, y]
     */
    getDisplayColorAt(position) {
        const canvas = $("#pyswitch-display");
        if (!canvas) throw new Error("Display not found");

        const ctx = canvas[0].getContext('2d');
        const p = ctx.getImageData(position[0], position[1], 1, 1).data; 
        
        return [p[0], p[1], p[2]];
    }

    /**
     * Returns the switch element for a switch ID as defined in the mappings.
     */
    #getSwitchElement(switchDef) {
        const switchElement = $("#pyswitch-switch-" + switchDef.port);
        if (switchElement.attr('id') != "pyswitch-switch-" + switchDef.port) throw new Error("Switch " + switchDef.port + " not found");
        return switchElement;
    }

    /**
     * Returns the LED element for a pixel ID as defined in the mappings.
     */
    #getLedElements(switchDef) {
        const ret = [];
        for (const led of switchDef.pixels) {
            const ledElement = $("#pyswitch-led-" + led);
            if (ledElement.attr('id') != "pyswitch-led-" + led) throw new Error("LED " + led + " not found");
            ret.push(ledElement);
        }
        return ret;
    }
}