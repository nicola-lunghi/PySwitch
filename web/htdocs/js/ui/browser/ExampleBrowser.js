class ExampleBrowser extends BrowserBase {

    #last = null;
    #toc = null;

    #build(items, entry) {
        const that = this;

        this.element.append(
            $('<div class="content" />').append(
                // Headline
                $('<div class="headline"/>')
                .text('Choose an example to run:'),

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
                    $('<span />').text("/examples" + entry.path)
                ),

                // Listing
                $('<table/>').append(
                    $('<tbody/>').append(items)
                ),

                // Close button
                $('<span class="fa fa-times close-button"/>')
                .on('click', async function() {
                    that.hide();
                })
            )
        );
    }

    /**
     * Show the browser
     */
    async browse(entry = null) {
        await this.#loadToc();        
            
        if (!entry) entry = this.#last ? this.#last : this.#toc;

        this.element.empty();

        if (entry.path == "pyswitch-default") {
            this.hide();
            this.controller.routing.call(this.controller.getControllerUrl(entry.path));
            return;
        }

        const listing = entry.children ? entry.children.filter((e) => e.type == "dir") : null; //await this.#getListing(entry);

        listing.sort(function (a, b) {
            if (a.name < b.name) return -1;
            if (a.name > b.name) return 1;
            return 0;
        });

        if (entry.isExample()) {
            this.hide();
            this.controller.routing.call(entry.getUrl());
            return;
        }

        if (listing.length == 1) {
            await this.browse(listing[0]);
            return;
        }
        
        const items = [];

        for(const e of listing) {
            items.push(e.getElement());
        }

        this.#build(items, entry);

        this.#last = entry;
        this.show();
    }

    /**
     * Load TOC for all examples if not yet loaded
     */
    async #loadToc() {
        if (this.#toc) return;

        // Load TOC data
        const toc = JSON.parse(await Tools.fetch("examples/toc.php"));
        
        // Build hierarchy
        const that = this;
        function crawl(entry, prefix) {
            const ret = new ExampleEntry(
                that,
                entry.name,
                prefix + entry.name,
                entry.type
            );

            for(const child_def of entry.children || []) {
                const child = crawl(child_def, prefix + entry.name + "/");
                child.parent = ret;
                ret.children.push(child);
            }

            return ret;
        }

        this.#toc = crawl(toc, "");
        
        // Add "Default PySwitch" option at root level
        this.#toc.children.unshift(
            new ExampleEntry(
                this,
                "PySwitch Default",
                "pyswitch-default",
                "dir",
                this.#toc
            )
        )
    }

    hide() {
        this.controller.ui.progress(1);
        super.hide();
    }
}