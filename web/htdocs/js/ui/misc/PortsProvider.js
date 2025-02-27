/**
 * Data provider for popups for choosing from MIDI ports
 */
class PortsProvider extends BrowserProvider {

    #toc = null;
    #options = null;
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
    constructor(controller, options) {
        super();
        this.#controller = controller;
        this.#options = options;
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
                text: this.#options.rootText
            }
        );

        for (const c of controllers) {
            this.#toc.children.push(
                new BrowserEntry(
                    browser,
                    {
                        value: c.name,
                        parent: this.#toc,
                        onSelect: this.#options.onSelect
                    }
                )
            )
        }

        // Additional entries
        for (const e of this.#options.additionalEntries || []) {
            e.parent = this.#toc;
            if (!e.onSelect) e.onSelect = this.#options.onSelect;

            this.#toc.children.push(
                new BrowserEntry(browser, e)
            )
        }

        return this.#toc;
    }
}