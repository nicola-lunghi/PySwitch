/**
 * Data provider for showing one single entry
 */
class SingleEntryProvider extends BrowserProvider {

    #options = null;

    /**
     * {
     *      text:
     *      onSelect:           (entry) => void,
     *      showCallback:       bool function, if the entry should be shown
     *      sortString
     * }
     */
    constructor(options) {
        super();
        this.#options = options;
    }

    /**
     * Return TOC for the controllers
     */
    async getToc(browser) {
        if (this.#options.showCallback) {
            if (!(await this.#options.showCallback())) return null;
        }

        return new BrowserEntry(
            browser,
            {
                text: this.#options.text,
                onSelect: this.#options.onSelect,
                sortString: this.#options.sortString ? this.#options.sortString : null
            }
        );
    }
}