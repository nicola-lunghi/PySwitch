class ExamplesProvider extends BrowserProvider {
    
    #toc = null;
    #path = null;

    constructor(path) {
        super();
        this.#path = path;
    }

    /**
     * Return TOC for all examples if not yet loaded
     */
    async getToc(browser) {
        if (this.#toc) return this.#toc;

        // Load TOC data
        const toc = JSON.parse(await Tools.fetch(this.#path));
        
        /**
         * Select the entry
         */
        function onSelect(entry) {
            browser.controller.routing.call(encodeURI("example" + entry.config.callPath));
        }
        
        // Build hierarchy        
        function crawl(entry, prefix) {
            // Make it a callable entry if it is a folder and does not have any subfolders
            if (entry.type == "dir" && !entry.children.filter((e) => e.type == "dir").length) {
                // Example
                return new BrowserEntry(
                    browser,
                    {
                        value: entry.name,                        
                        callPath: prefix + entry.name,
                        onSelect: onSelect,
                        toc: entry
                    }                    
                );
            }

            // Folder
            const ret = new BrowserEntry(
                browser,
                {
                    value: entry.name,
                    callPath: prefix + entry.name,
                    childLayout: [
                        // Type icon
                        {
                            type: "typeIcon"
                        },
        
                        // README icon
                        {
                            get: function(entry) {
                                return !entry.isCallable() ? null : 
                                    $('<span class="fa"/>')
                                    .addClass("fa-info")
                                    .on('click', async function() {
                                        try {
                                            window.open('examples' + entry.config.callPath + '/README.md', '_blank');
        
                                        } catch (e) {
                                            browser.controller.handle(e);
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

            for(const child_def of entry.children || []) {
                // Exclude MIDI Routing examples
                if (child_def.name.includes("MIDI Routings")) continue;

                const child = crawl(child_def, prefix + entry.name + "/");
                child.parent = ret;
                ret.children.push(child);
            }

            return ret;
        }

        const examples = crawl(toc, "");
        examples.text = "PySwitch Examples";

        // Add "Default PySwitch" option at root level
        examples.children.unshift(
            new BrowserEntry(
                browser,
                {
                    value: "PySwitch Default",
                    onSelect: async function(/*entry*/) {
                        try {
                            browser.controller.routing.call(browser.controller.getControllerUrl("pyswitch-default"));

                        } catch (e) {
                            browser.controller.handle(e);
                        }
                    },
                    parent: examples
                }
            )
        )

        this.#toc = examples;
        return examples;
    }
}