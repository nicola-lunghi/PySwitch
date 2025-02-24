class PortsProvider extends BrowserProvider {

    #toc = null;
    #config = null;
    #controller = null;

    /**
     * {
     *      onSelect:           (entry) => void,
     *      additionalEntries:  Array of additional entries like 
     *                          {
     *                              ...all otions of BrowserEntry (except parent which will be overwritten)
     *                          }
     *      rootText:           Text for the root entry (optional, can be a callback(entry) => string)
     * }
     */
    constructor(controller, config) {
        super();
        this.#controller = controller;
        this.#config = config;
    }

    /**
     * Return TOC for the controllers
     */
    async getToc(browser) {
        if (this.#toc) return this.#toc;

        const controllers = await this.#controller.midi.getMatchingPortPairs();

        this.#toc = new BrowserEntry(
            browser,
            {
                text: this.#config.rootText
            }
        );

        for (const c of controllers) {
            this.#toc.children.push(
                new BrowserEntry(
                    browser,
                    {
                        value: c.name,
                        parent: this.#toc,
                        onSelect: this.#config.onSelect
                    }
                )
            )
        }

        // Additional entries
        for (const e of this.#config.additionalEntries || []) {
            e.parent = this.#toc;
            if (!e.onSelect) e.onSelect = this.#config.onSelect;

            this.#toc.children.push(
                new BrowserEntry(browser, e)
            )
        }

        return this.#toc;
    }
}