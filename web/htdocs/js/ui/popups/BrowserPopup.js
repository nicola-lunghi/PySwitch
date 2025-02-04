class BrowserPopup extends Popup {

    #last = null;
    #toc = null;

    /**
     * config: {
     *      container:   Container DOM element (can be shared!)
     *      headline:    Header text   
     *      providers:   Array of provider instances,
     *      postProcess: Optional callback to alter the generated DOM: postProcess(entry, generatedElement) => void
     * }
     */
    constructor(controller, config) {
        super(controller, config);
    }

    /**
     * Show the browser
     */
    async browse(entry = null) {
        // Load data
        const toc = await this.#getData();

        // Show root if no element is passed
        if (!entry) entry = this.#last ? this.#last : toc;

        // If we are at a leaf, call if and return
        if (entry.isCallable()) {
            this.hide();
            await entry.call();
            return;
        }

        // Get sorted child list of the current entry
        const listing = entry.children ? entry.children.filter((e) => e.children.length || e.isCallable()) : [];

        listing.sort(function (a, b) {
            const aname = a.getSortString();
            const bname = b.getSortString();
            
            return aname.localeCompare(bname);
        });

        // Create DOM items for the children
        const items = [];
        for(const e of listing) {
            const el = e.getElement(entry.config.childLayout);            

            if (this.config.postProcess) {
                await this.config.postProcess(e, el);
            }

            items.push(el);
        }

        this.#last = entry;

        // Build DOM and show the browser
        this.show(
            this.#buildContent(items, entry),
            this.config.headline
        );
    }

    /**
     * Returns a TOC of all providers, if not done
     */
    async #getData() {
        if (this.#toc) return this.#toc;

        // One provider: Use this as root
        if (this.config.providers.length == 1) {
            this.#toc = await this.config.providers[0].getToc(this);
            return this.#toc;
        }

        // Multiple providers: Create new root and add all provider roots as children
        this.#toc = new BrowserEntry(this);

        for(const p of this.config.providers) {
            const child = await p.getToc(this);
            child.parent = this.#toc;
            this.#toc.children.push(child);
        }

        return this.#toc;
    }

    /**
     * Build the DOM (returns content for Popup)
     */
    #buildContent(items, entry) {
        const that = this;
        
        return [
            !(entry && entry.parent) ? null :
            $('<div class="path"/>').append(
                // Back button
                $('<span class="fa fa-chevron-left"/>')
                .on('click', async function() {
                    try {
                        await that.browse(entry.parent);

                    } catch (e) {
                        that.controller.handle(e);
                    }
                }),

                // Path display
                $('<span />').append(entry.getHierarchicalPath())
            ),

            // Listing
            $('<table/>').append(
                $('<tbody/>').append(items)
            )
        ]
    }
}