class ActionParserTests extends FunctionParserTestBase {

    async getAvailableActions() {
        await this.init();
        
        const basePath = "../";
        const that = this;

        await this.checkDefinitions(
            "actions.json",

            // Load from buffer file
            async function() {
                return JSON.parse(await Tools.fetch(basePath + "definitions/actions.json"));
            },

            // Generate from scratch
            async function() {
                const extractor = new FunctionExtractor(that.pyswitch);
        
                return extractor.get({
                    tocPath: basePath + "circuitpy/lib/pyswitch/clients/toc.php",
                    subPath: "kemper/actions",
                    targetPath: "pyswitch/clients/kemper/actions"
                })
            }
        )
    }

    async getAvailableActionsMeta() {
        const config = new MockConfiguration("", "");
        await config.init(this.pyswitch);
        const parser = config.parser;
        
        await this.checkDefinitions(
            "actions-with-meta.json",

            // Load from buffer file
            async function() {
                return JSON.parse(await Tools.fetch("data/definitions/actions-with-meta.json"));
            },

            // Generate from scratch
            async function() {
                return await parser.getAvailableActions("../");
            }
        )
    }
}