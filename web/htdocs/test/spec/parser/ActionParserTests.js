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
        
                const clients = await Client.getAvailable(basePath);

                const ret = [];
                for (const client of clients) {
                    let actions = await extractor.get({
                        tocPath: basePath + "circuitpy/lib/pyswitch/clients/toc.php",
                        subPath: client.id + "/actions",
                        targetPath: "pyswitch/clients/" + client.id + "/actions"
                    });

                    // Add actions from __init__.py
                    if (client.getInitActionsClassName()) {
                        const __init__extractor = new ClassAttributeExtractor(that.pyswitch);

                        const init_actions = await __init__extractor.get({
                            file: "pyswitch/clients/" + client.id + "/__init__.py",
                            importPath: "pyswitch.clients." + client.id,
                            className: client.getInitActionsClassName()
                        });

                        actions = actions.concat(init_actions);
                    }

                    ret.push({
                        client: client.id,
                        actions: actions
                    })
                }
                return ret;
            }
        )
    }

    // async getAvailableActionsMeta() {
    //     await this.init();
        
    //     const config = new MockConfiguration("", "");
    //     await config.init(this.pyswitch);
    //     const parser = config.parser;
        
    //     await this.checkDefinitions(
    //         "actions-with-meta.json",

    //         // Load from buffer file
    //         async function() {
    //             return JSON.parse(await Tools.fetch("data/definitions/actions-with-meta.json"));
    //         },

    //         // Generate from scratch
    //         async function() {
    //             return await parser.getAvailableActions("../");
    //         }
    //     )
    // }
}