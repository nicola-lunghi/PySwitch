class ActionsProvider extends BrowserProvider {

    #toc = null;
    #parser = null;
    #config = null;
    
    /**
     * {
     *      onSelect
     * }
     */
    constructor(parser, config) {
        super();
        this.#parser = parser;
        this.#config = config;
    }

    /**
     * Return TOC for the controllers
     */
    async getToc(browser) {
        if (this.#toc) return this.#toc;

        const actions = await this.#parser.getAvailableActions();

        this.#toc = new BrowserEntry(
            browser,
            {
                childLayout: [
                    {
                        get: async function(entry) {
                            // Listing entry link
                            return $('<span class="listing-link" />')
                                .addClass("category-" + entry.config.model.meta.getCategory())
                                .text(await entry.getText())
                                .on('click', async function() {
                                    try {
                                        await browser.browse(entry);

                                    } catch (e) {
                                        console.error(e);
                                    }
                                });
                        }
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
                        onSelect: this.#config.onSelect,
                        model: action,
                        sortString: this.#parser.getActionSortString(action)
                    }
                )
            )
        }

        return this.#toc;
    }    
}