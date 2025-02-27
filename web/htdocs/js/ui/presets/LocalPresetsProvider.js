/**
 * Data provider for managing local storage presets
 */
class LocalPresetsProvider extends BrowserProvider {

    #toc = null;
    #options = null;

    #presets = null;

    /**
     * {
     *      onSelect,
     *      newPresetsEntry: false
     * }
     */
    constructor(options) {
        super();
        this.#options = options;

        this.#presets = new Presets();
    }

    /**
     * Return TOC for the presets
     */
    async getToc(browser) {
        if (this.#toc) return this.#toc;

        this.#toc = new BrowserEntry(
            browser,
            {
                text: "Presets"
                // childLayout: [
                //     {
                //         get: async function(entry) {
                //             // Listing entry link
                //             return $('<span class="listing-link" />')
                //                 .addClass("category-" + entry.data.actionDefinition.meta.getCategory())
                //                 .text(await entry.getText())
                //                 .on('click', async function() {
                //                     try {
                //                         await browser.browse(entry);

                //                     } catch (e) {
                //                         console.error(e);
                //                     }
                //                 });
                //         }
                //     }
                // ]
            }
        );

        const presets = this.#presets.getAll();
        
        for (const preset of presets) {
            this.#toc.children.push(
                new BrowserEntry(
                    browser,
                    {
                        text: preset,
                        value: preset,
                        parent: this.#toc,
                        onSelect: this.#options.onSelect
                    }
                )
            )
        }

        // New 
        if (this.#options.newPresetsEntry) {
            this.#toc.children.push(
                new BrowserEntry(
                    browser,
                    {
                        text: "New Preset...",
                        newPreset: true,
                        parent: this.#toc,
                        onSelect: this.#options.onSelect
                    }
                )
            )
        }

        return this.#toc;
    }    
}