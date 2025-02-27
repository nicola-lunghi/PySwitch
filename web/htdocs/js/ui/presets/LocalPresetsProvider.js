/**
 * Data provider for managing local storage presets
 */
class LocalPresetsProvider extends BrowserProvider {

    // #toc = null;
    #options = null;

    #controller = null;

    /**
     * {
     *      onSelect,
     *      newPresetsEntry: false
     * }
     */
    constructor(controller, options) {
        super();
        this.#options = options;

        this.#controller = controller;
    }

    /**
     * Return TOC for the presets
     */
    async getToc(browser) {
        //if (this.#toc) return this.#toc;
        const that = this;

        const toc = new BrowserEntry(
            browser,
            {
                text: "Presets",
                childLayout: [
                    // Type icon
                    {
                        type: "typeIcon"
                    },

                    // Delete icon
                    {
                        get: function(entry) {                            
                            return (!entry.isCallable() || entry.data.newPreset) ? null : 
                                $('<span class="clickable fa fa-trash" data-toggle="tooltip" title="Delete preset..."/>')
                                .on('click', async function() {
                                    try {
                                        if (!confirm("Do you want to delete preset " + entry.text + "?")) return;

                                        that.#controller.presets.delete(entry.value);

                                        await browser.browse();  // Reloads the toc

                                        that.#controller.ui.notifications.message("Successfully deleted preset " + entry.text, "S");

                                    } catch (e) {
                                        browser.handle(e);
                                    }
                                })
                        }
                    },

                    // Rename icon
                    {
                        get: function(entry) {                            
                            return (!entry.isCallable() || entry.data.newPreset) ? null : 
                                $('<span class="clickable fa fa-pen" data-toggle="tooltip" title="Rename preset..."/>')
                                .on('click', async function() {
                                    try {
                                        const newName = prompt("New name for " + entry.text + ":", entry.value);
                                        if (!newName) return;

                                        const data = that.#controller.presets.get(entry.value);
                                        that.#controller.presets.delete(entry.value);
                                        that.#controller.presets.set(newName, data);

                                        await browser.browse();  // Reloads the toc

                                        that.#controller.ui.notifications.message("Successfully renamed preset " + entry.text + " to " + newName, "S");

                                    } catch (e) {
                                        browser.handle(e);
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

        const presets = this.#controller.presets.getAll();
        
        for (const presetId of presets) {
            toc.children.push(
                new BrowserEntry(
                    browser,
                    {
                        text: presetId,
                        value: presetId,
                        parent: toc,
                        onSelect: this.#options.onSelect
                    }
                )
            )
        }

        // New 
        if (this.#options.newPresetsEntry) {
            toc.children.push(
                new BrowserEntry(
                    browser,
                    {
                        text: "New Preset...",
                        newPreset: true,
                        parent: toc,
                        onSelect: this.#options.onSelect,
                        sortString: "___________________"
                    }
                )
            )
        }

        return toc;
    }    
}