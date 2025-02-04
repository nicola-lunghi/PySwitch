class ExampleTestRunner {

    /**
     * Process the tests. This loads a TOC of all tests and executes one after another, 
     * with behavioural mocks testing the functionality.
     */
    async process() {
        const toc = await Tools.fetch("../examples/toc.php");

        console.log(toc)
    }
}