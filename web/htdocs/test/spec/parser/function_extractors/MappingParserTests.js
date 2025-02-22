class MappingParserTests extends FunctionParserTestBase {

    async getAvailableMappings() {
        await this.init();
        
        const basePath = "../";
        const that = this;

        await this.checkDefinitions(
            "mappings.json",

            // Load from buffer file
            async function() {
                return JSON.parse(await Tools.fetch(basePath + "definitions/mappings.json"));
            },

            // Generate from scratch
            async function() {
                const extractor = new FunctionExtractor(that.pyswitch);
        
                return extractor.get({
                    tocPath: basePath + "circuitpy/lib/pyswitch/clients/toc.php",
                    subPath: "kemper/mappings",
                    targetPath: "pyswitch/clients/kemper/mappings"
                })
            }
        )
    }

    async getAvailableMappingsMeta() {
        const config = new MockConfiguration("", "");
        await config.init(this.pyswitch);
        const parser = config.parser;
        
        await this.checkDefinitions(
            "mappings-with-meta.json",

            // Load from buffer file
            async function() {
                return JSON.parse(await Tools.fetch("data/definitions/mappings-with-meta.json"));
            },

            // Generate from scratch
            async function() {
                return await parser.getAvailableMappings("../");
            }
        )
    }
}