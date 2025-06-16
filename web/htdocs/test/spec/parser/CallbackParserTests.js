class CallbackParserTests extends FunctionParserTestBase {

    async getAvailableDisplayLabelCallbacks() {
        await this.init();
        
        const basePath = "../";
        // const that = this;

        const extractor = new ClassNamesExtractor(this.pyswitch);
        const itemExtractor = new ClassItemExtractor(this.pyswitch);        
        const clients = await Client.getAvailable(basePath);

        // async function fromClass(options) {
        //     const extractor = new ClassItemExtractor(that.pyswitch);
        //     return await extractor.get(options);
        // }
        
        async function cleanClasses(classes) {
            const ret = [];
            for (const cls of classes) {
                const items = await itemExtractor.get({
                    file: cls.importPath.replaceAll('.', '/') + ".py",
                    className: cls.name,
                    importPath: cls.importPath,
                    functions: true,
                    includeUnderscore: true  
                });

                for (const item of items) {
                    if (item.name.includes('.')) continue;

                    cls.parameters = item.parameters;

                    ret.push(cls);
                    break;
                }
            }
            return ret;
        }

        await this.checkDefinitions(
            "callbacks.json",

            // Load from buffer file
            async function() {
                return JSON.parse(await Tools.fetch(basePath + "definitions/callbacks.json"));
            },

            // Generate from scratch
            async function() {
                const ret = [];
                for (const client of clients) {
                    let classes = await extractor.get({
                        tocPath: basePath + "circuitpy/lib/pyswitch/clients/toc.php",
                        subPath: client.id + "/callbacks",
                        targetPath: "pyswitch/clients/" + client.id + "/callbacks"
                    });

                    const classesCleaned = await cleanClasses(classes);

                    // // Add callbacks from __init__.py
                    // if (client.getInitActionsClassName()) {
                    //     actions = actions.concat(await fromClass({
                    //         file: "pyswitch/clients/" + client.id + "/__init__.py",
                    //         importPath: "pyswitch.clients." + client.id,
                    //         className: client.getInitActionsClassName(),
                    //         functions: true
                    //     }))
                    // }

                    ret.push({
                        client: client.id,
                        callbacks: classesCleaned
                    })
                }

                return ret;
            }
        )
    }
}