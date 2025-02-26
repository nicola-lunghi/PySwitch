/**
 * Data provider for add/edit actions (to be used in BrowserPopups)
 */
class ActionsProvider extends BrowserProvider {

    #toc = null;
    #parser = null;
    #config = null;

    preselectEntry = null;
    
    /**
     * {
     *      onSelect,
     *      preselectActionName
     * }
     */
    constructor(parser, config) {
        super();
        this.#parser = parser;
        this.#config = config;
    }

    /**
     * Return TOC for the actions
     */
    async getToc(browser) {
        if (this.#toc) return this.#toc;

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

        const clients = await this.#parser.getAvailableActions();
        
        for (const client of clients) {
            for (const action of client.actions) {
                const entry = new BrowserEntry(
                    browser,
                    {
                        text: action.meta.getDisplayName(),
                        value: action.name,
                        parent: this.#toc,
                        onSelect: this.#config.onSelect,
                        model: action,
                        sortString: await action.meta.client.getActionSortString(action)
                    }
                )

                if (this.#config.preselectActionName && (action.name == this.#config.preselectActionName)) {
                    this.preselectEntry = entry;
                } 

                this.#toc.children.push(
                    entry
                )
            }
        }

        return this.#toc;
    }    
}