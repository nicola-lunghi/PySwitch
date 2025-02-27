/**
 * Provider for browser popups, loading the templates for creating new configurations.
 */
class TemplatesProvider extends BrowserProvider {
    
    #toc = null;
    #path = null;
    #controller = null;

    constructor(controller, path) {
        super();
        this.#controller = controller;
        this.#path = path;
    }

    /**
     * Return TOC for all examples if not yet loaded
     */
    async getToc(browser) {
        if (this.#toc) return this.#toc;

        // Load TOC data
        const toc = JSON.parse(await Tools.fetch(this.#path));
        
        const that = this;

        /**
         * Select the entry
         */
        function onSelect(entry) {
            that.#controller.routing.call(encodeURI("template" + entry.data.callPath));
        }
        
        // Build hierarchy        
        function crawl(entry, prefix) {
            // Make it a callable entry if it is a folder and does not have any subfolders
            if (entry.type == "dir" && !entry.children.filter((e) => e.type == "dir").length) {
                // Template
                return new BrowserEntry(
                    browser,
                    {
                        value: entry.name,                        
                        callPath: prefix + entry.name,
                        onSelect: onSelect
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
        
                        // Link
                        {
                            type: "link"
                        }
                    ]
                }
            );

            for(const child_def of entry.children || []) {
                const child = crawl(child_def, prefix + entry.name + "/");
                child.parent = ret;
                ret.children.push(child);
            }

            return ret;
        }

        this.#toc = crawl(toc, "");
        
        this.#toc.text = "Create new...";
        this.#toc.data.sortString = "_____________";
        
        return this.#toc;
    }
}