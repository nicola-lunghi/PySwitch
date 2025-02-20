class BrowserPopup extends Popup {

    #last = null;
    #toc = null;
    #infoPanel = null;
    #infoPanelContent = null;
    #infoPanelOnClick = null;

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
        let listing = entry.children ? entry.children.filter((e) => e.children.length || e.isCallable()) : [];

        // Sort it
        listing = await this.#sort(listing);

        // Create DOM items for the children
        const items = [];
        for(const e of listing) {
            const el = await e.getElement(entry.config.childLayout);            

            if (this.config.postProcess) {
                await this.config.postProcess(e, el);
            }

            items.push(el);
        }

        this.#last = entry;

        // Build DOM and show the browser
        this.show(
            await this.#buildContent(items, entry),
            this.config.headline
        );
    }

    /**
     * Toggle visibility of the info panel
     */
    showInfoPanel(content, onClick = null) {
        this.#infoPanelContent.html(content);
        this.#infoPanelOnClick = onClick;

        this.#infoPanel.toggleClass('clickable', !!onClick);

        this.#infoPanel.show();                
    }

    /**
     * Sort the listing of entries (Schwartzian transform). Returns the sorted array.
     * https://stackoverflow.com/questions/45661247/implement-async-await-in-sort-function-of-arrays-javascript
     */
    async #sort(listing) {
        // Get an array with [sortString, entry] instead of each entry
        const comparableArray = await Promise.all(
            listing.map(
                async x => [await x.getSortString(), x]
            )
        );

        // Sort
        comparableArray.sort(function (a, b) {
            const aname = a[0]; //.getSortString();
            const bname = b[0]; //.getSortString();
            return aname.localeCompare(bname);
        });

        // Transform back into original form
        return comparableArray.map(x => x[1]);
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
    async #buildContent(items, entry) {
        const that = this;
        
        return $('<div class="browser-content" />').append(
            [
                $('<div class="path"/>').append(
                    !(entry && entry.parent) ? null :
                    [
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
                        $('<span />').append(await entry.getHierarchicalPath())
                    ]
                ),

                // Listing
                $('<div class="table-container" />').append(
                    $('<table/>').append(
                        $('<tbody/>').append(items)
                    )
                ),

                // Info panel
                this.#infoPanel = $('<div class="info-panel" />').append(
                    this.#infoPanelContent = $('<div />')
                )
                .on('click', async function() {
                    await that.#onInfoPanelClick();
                })
                .hide()
            ]
        )
    }

    async #onInfoPanelClick() {
        if (this.#infoPanelOnClick) {
            await this.#infoPanelOnClick();
        }
    }
}