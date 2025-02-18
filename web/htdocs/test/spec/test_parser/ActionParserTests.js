class ActionParserTests {

    pyswitch = null;    // Shared python runner

    
    /**
     * Must be called before any of the tests can be run
     */
    async #init() {
        if (this.pyswitch) return;

        this.pyswitch = new PySwitchRunner(
            {
                domNamespace: "pyswitch",
                updateIntervalMillis: 10
            }, 
            "test-pyswitch-example"
        );

        await this.pyswitch.init("../");
    }
}