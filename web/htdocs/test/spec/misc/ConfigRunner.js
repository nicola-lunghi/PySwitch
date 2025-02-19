class ConfigRunner {
    
    pyswitch = null;
    timeMillis = 0;
    client = null;

    constructor(pyswitch) {
        this.pyswitch = pyswitch;        
    }

    /**
     * Runs the config in PySwitch. 
     * 
     * async performTestsCallback() => void
     */
    async run(config, performTestsCallback = null) {
        this.client = null;

        // Create a temporary container element for pyswitch
        const el = $('<div id="test-pyswitch-example" />');
        $('body').append(el);

        // Set up frontend
        const frontend = new PySwitchFrontend(null, el, { domNamespace: "pyswitch" });
        await frontend.apply(await config.parser(this.pyswitch));

        // Reset virtual simulation time
        this.timeMillis = 0;

        // Set up virtual client
        const that = this;
        this.client = await VirtualClient.getInstance(config, {
            overrideTimeCallback: function() {
                return that.timeMillis;
            }
        });

        // Set client as MIDI wrapper to connect it to PySwitch
        this.pyswitch.setMidiWrapper(this.client);
        
        // Override current time
        this.pyswitch.setTimeCallback(function() {
            return that.timeMillis / 1000;
        });

        // Run without ticking
        await this.pyswitch.run(await config.get(), true);

        // Do the tests
        if (performTestsCallback) {
            await performTestsCallback();
        } else {
            // Do some few initial ticks to check everything is up and running
            let i = 0;
            while(i++ < 5) {
                await this.tick();
            }
        }    

        // Remove the test element from the body again
        el.remove();
    }

    /**
     * Execute one tick for a given amount of milliseconds (default is one second).
     */
    async tick(stepMillis = 100) {
        this.timeMillis += stepMillis;

        await this.pyswitch.tick();

        if (this.client) {
            await this.client.update();
        }
    }
}