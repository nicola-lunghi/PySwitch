class ExampleTestRunner {

    pyswitch = null;

    #examplesPath = "../examples";         // Path to the examples folder

    constructor() {
        this.pyswitch = new PySwitchRunner({
            domNamespace: "pyswitch",
            updateIntervalMillis: 10
        }, null);
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
     * Tests on BrowserEntry which contains an example
     */
    async #testExample(entry) {
        if (!entry.config.callPath) {
            console.warn("Skip example without callPath: ", entry);
            return;
        };

        // Load config files
        const inputs_py = await Tools.fetch(this.#examplesPath + entry.config.callPath + "/inputs.py");
        const display_py = await Tools.fetch(this.#examplesPath + entry.config.callPath + "/display.py");
        
        
    }
}