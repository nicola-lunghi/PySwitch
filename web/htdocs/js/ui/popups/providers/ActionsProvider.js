class ActionsProvider extends BrowserProvider {

    #toc = null;
    #parser = null;
    #controller = null;
    #frontend = null;
    #input = null;
    
    constructor(controller, frontend, parser, input) {
        super();
        this.#controller = controller;
        this.#frontend = frontend;
        this.#parser = parser;
        this.#input = input;
    }

    /**
     * Return TOC for the controllers
     */
    async getToc(browser) {
        if (this.#toc) return this.#toc;

        const actions = await this.#parser.getAvailableActions();

        const that = this;
        this.#toc = new BrowserEntry(
            browser,
            {
                childLayout: [
                    // Type icon
                    {
                        type: "typeIcon"
                    },
    
                    // Info icon
                    {
                        get: function(entry) {
                            return !entry.isCallable() ? null : 
                                $('<span class="fa"/>')
                                .addClass("fa-info")
                                .on('click', async function() {
                                    try {
                                        const content = entry.config.model.comment ? entry.config.model.comment : "No info available";

                                        browser.showInfoPanel(content.replace("\n", "<br><br>"));
                                        
                                    } catch (e) {
                                        that.#controller.handle(e);
                                    }
                                })
                        }
                    },
    
                    // Link
                    {
                        type: "link"
                    }
                ]
            }
        );

        for (const action of actions) {
            const meta = new Meta(action);

            this.#toc.children.push(
                new BrowserEntry(
                    browser,
                    {
                        text: meta.getDisplayName(),
                        value: action.name,
                        parent: this.#toc,
                        onSelect: async function(entry) {
                            await that.#frontend.addAction({
                                name: entry.config.model.name,
                                arguments: entry.config.model.parameters.map((item) => { 
                                    return {
                                        name: item.name,
                                        value: item.meta.getDefaultValue()
                                    }
                                })
                            }, that.#input);
                        },
                        model: action
                    }
                )
            )
        }

        return this.#toc;
    }
}