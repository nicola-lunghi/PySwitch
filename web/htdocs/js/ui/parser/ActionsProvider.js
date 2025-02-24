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

        this.#toc = new BrowserEntry(browser);

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
                        model: action
                    }
                )
            )
        }

        return this.#toc;
    }
}