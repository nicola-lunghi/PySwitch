/**
 * Data provider for add/edit actions (to be used in BrowserPopups)
 */
class ActionsProvider extends BrowserProvider {

    #toc = null;
    #parser = null;
    #options = null;

    preselectEntry = null;
    
    /**
     * {
     *      onSelect,
     *      preselectActionName,     // Name of the action to preselect
     *      target                   // The target hardware model name, e.g. AdafruitSwitch
     * }
     */
    constructor(parser, options) {
        super();
        this.#parser = parser;
        this.#options = options;        
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
                                .addClass("category-" + entry.data.actionDefinition.meta.getCategory())
                                .text(await entry.getText())
                                .on('click', async function() {
                                    try {
                                        await browser.browse(entry);

                                    } catch (e) {
                                        browser.handle(e);
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
                if (action.meta.data.target != this.#options.target) continue;

                const entry = new BrowserEntry(
                    browser,
                    {
                        text: action.meta.getDisplayName(),
                        value: action.name,
                        parent: this.#toc,
                        onSelect: this.#options.onSelect,
                        actionDefinition: action,
                        sortString: await action.meta.getSortString()
                    }
                )

                // Pre-selection by option
                if (this.#options.preselectActionName && (action.name == this.#options.preselectActionName)) {
                    this.preselectEntry = entry;
                }                 

                this.#toc.children.push(
                    entry
                )
            }
        }

        // Pre-select if we only have one entry
        if (this.#toc.children.length == 1) {
            this.preselectEntry = this.#toc.children[0];
        }

        return this.#toc;
    }    
}