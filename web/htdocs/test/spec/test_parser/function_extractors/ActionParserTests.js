class ActionParserTests extends FunctionParserTestBase {

    async getAvailableActions() {
        await this.init();
        
        const config = new MockConfiguration("", "");
        const parser = await config.parser(this.pyswitch);

        const basePath = "../";
        const that = this;

        await this.checkDefinitions(
            "actions.json",

            // Load from buffer file
            async function() {
                return await parser.getAvailableActions(basePath);
            },

            // Generate from scratch
            async function() {
                return await that.generateAvailableActions(basePath);
            }
        )
    }

    /**
     * Generates the actions definitions file from scratch
     */
    async generateAvailableActions(basePath) {
        const extractor = new FunctionExtractor(this.pyswitch);
        
        return extractor.get({
            tocPath: basePath + "circuitpy/lib/pyswitch/clients/toc.php",
            subPath: "kemper/actions",
            targetPath: "pyswitch/clients/kemper/actions"
        })
    }
}