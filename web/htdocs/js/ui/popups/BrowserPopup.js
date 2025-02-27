/**
 * Popup for browsing TOCs
 */
class BrowserPopup extends Popup {

    #toc = null;

    #buttons = null;
    #infoPanel = null;
    #infoPanelContent = null;
    #infoPanelOnClick = null;
    
    #last = null;
    #currentItems = null;

    /**
     * {
     *      container:                Container DOM element
     *      headline:                 Header text   
     *      providers:                Array of provider instances,
     *      selectedValue:            If set, the entry with this value will be selected until this value is changed. 
     *                                For temporary selection use setSelected() or setSelectedValue().
     *      dontCloseOnSelect: false
     *      onReturnKey:              Callback when the user hits the Return key
     * }
     */
    constructor(options) {
        super(options);
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
            if (!this.options.dontCloseOnSelect) this.hide();
            await entry.call();
            return;
        }

        // Get sorted child list of the current entry
        let listing = entry.children ? entry.children.filter((e) => e.children.length || e.isCallable()) : [];

        // Sort it
        listing = await this.#sort(listing);

        // Create DOM items for the children
        this.#currentItems = [];
        for(const e of listing) {
            const el = await e.getElement(entry.data.childLayout);            

            this.#currentItems.push({
                entry: e,
                element: el
            });
        }

        this.#last = entry;

        // Build DOM and show the browser
        this.show(
            await this.#buildContent(entry),
            this.options.headline
        );

        if (this.options.selectedValue) {
            this.setSelectedValue(this.options.selectedValue);
        }
    }

    /**
     * Toggle visibility of the info panel
     */
    showInfoPanel(content) {
        this.#infoPanelContent.empty();
        this.#infoPanelContent.append(content);        
        this.#infoPanel.show();                
    }

    /**
     * Set selection by value
     */
    setSelectedValue(value) {
        for (const item of this.#currentItems) {
            item.element.toggleClass("selected", item.entry.value == value);
        }
    }

    /**
     * Set selection by entry
     */
    setSelected(entry) {
        for (const item of this.#currentItems) {
            item.element.toggleClass("selected", item.entry == entry);
        }
    }

    /**
     * Adds some buttons, replacing the old ones
     */
    setButtons(buttons) {
        if (!this.#buttons) throw new Error("Popup not initialized with show()");

        this.#buttons.empty();

        if (buttons) {
            this.#buttons.append(buttons);
            this.#buttons.show();
        } else {
            this.#buttons.hide();
        }
    }

    /**
     * Sort the listing of entries (Schwartzian transform). Returns the sorted array.
     * https://stackoverflow.com/questions/45661247/implement-async-await-in-sort-function-of-arrays-javascript
     */
    async #sort(listing) {
        // Get an array with [sortString, entry] instead of each entry
        const comparableArray = await Promise.all(
            listing.map(
                async entry => [await entry.getSortString(), entry]
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
        if (this.options.providers.length == 1) {
            this.#toc = await this.options.providers[0].getToc(this);
            return this.#toc;
        }

        // Multiple providers: Create new root and add all provider roots as children
        this.#toc = new BrowserEntry(this);

        for(const p of this.options.providers) {
            const child = await p.getToc(this);
            child.parent = this.#toc;
            this.#toc.children.push(child);
        }

        return this.#toc;
    }

    /**
     * Build the DOM (returns content for Popup)
     */
    async #buildContent(entry) {
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
                                console.error(e);
                            }
                        }),

                        // Path display
                        $('<span />').append(await entry.getHierarchicalPath())
                    ]
                ),

                // Listing
                $('<div class="table-container" />').append(
                    $('<table/>').append(
                        $('<tbody/>').append(
                            this.#currentItems.map((item) => item.element)
                        )
                    )
                ),

                // Info panel
                $('<div class="right-side" />').append(
                    this.#infoPanel = $('<div class="info-panel" />').append(
                        this.#infoPanelContent = $('<div />')
                    )
                    .on('click', async function() {
                        try {
                            await that.#onInfoPanelClick();
                            
                        } catch (e) {
                            console.error(e);
                        }
                    })
                    .hide(),
                    
                    // Buttons
                    this.#buttons = $('<div class="buttons" />').hide()
                )
            ]
        )
    }

    async #onInfoPanelClick() {
        if (this.#infoPanelOnClick) {
            await this.#infoPanelOnClick();
        }
    }
}