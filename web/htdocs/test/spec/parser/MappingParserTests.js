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

                const mappings = await extractor.get({
                    tocPath: basePath + "circuitpy/lib/pyswitch/clients/toc.php",
                    subPath: "kemper/mappings",
                    targetPath: "pyswitch/clients/kemper/mappings"
                })

                // Add mappings from __init__.py
                const __init__extractor = new ClassAttributeExtractor(that.pyswitch);

                const init_mappings = await __init__extractor.get({
                    file: "pyswitch/clients/kemper/__init__.py",
                    importPath: "pyswitch.clients.kemper",
                    className: "KemperMappings"
                });

                return mappings.concat(init_mappings);
            }
        )
    }

    // async getAvailableMappingsMeta() {
    //     await this.init();
        
    //     const config = new MockConfiguration("", "");
    //     await config.init(this.pyswitch);
    //     const parser = config.parser;
        
    //     await this.checkDefinitions(
    //         "mappings-with-meta.json",

    //         // Load from buffer file
    //         async function() {
    //             return JSON.parse(await Tools.fetch("data/definitions/mappings-with-meta.json"));
    //         },

    //         // Generate from scratch
    //         async function() {
    //             return await parser.getAvailableMappings("../");
    //         }
    //     )
    // }
}