class ExampleBrowser {

    #element = null;
    #controller = null;

    #toc = null;

    constructor(controller, element) {
        this.#controller = controller;
        this.#element = element;
    }

    #build(items, pathText, backPath) {
        const that = this;

        this.#element.append(
            // Headline
            $('<div class="headline"/>')
            .text('Choose an example to run:'),

            $('<div class="path"/>').append(
                // Back button
                $('<span class="fa fa-chevron-left"/>')
                .on('click', async function() {
                    if (!backPath) return;

                    that.#controller.routing.call(backPath);
                }),

                // Path display
                $('<span />').text(pathText)
            ),

            // Listing
            $('<table/>').append(
                $('<tbody/>').append(items)
            ),

            // Close button
            $('<span class="fa fa-times close-button"/>')
            .on('click', async function() {
                that.#controller.routing.home();
            })
        );
    }

    /**
     * Show the browser to browse the contents of path inside the examples folder
     */
    async browse(path) {
        this.#controller.ui.block();
        this.#element.empty();

        const listing = await this.#getListing(path);
        
        if (listing.length == 1) {
            this.#controller.routing.call(this.#getExampleUrl(listing[0].path));
            return;
        }
        
        const items = [];
        for(const entry of listing) {
            items.push(this.#getListingElement(entry));
        }

        const backPath = this.#getBackPath(path);

        this.#build(items, "/examples/" + path, backPath);

        this.show();
    }

    /**
     * Gets the path for navigation to the parent
     */
    #getBackPath(path) {
        const splt = path.split("/");
        splt.pop();
        const j = splt.join("/");
        return this.#getExampleUrl("/" + j);
    }

    hide() {
        this.#element.hide();
    }

    show() {
        this.#element.show();
    }

    /**
     * Load TOC for all examples if not yet loaded
     */
    async #loadToc() {
        if (this.#toc) return;

        this.#toc = JSON.parse(await Tools.fetch("examples/toc.php"));
        
        // Get paths
        function crawl(entry, prefix) {
            entry.path = prefix + entry.name;

            for(const child of entry.children || []) {
                crawl(child, prefix + entry.name + "/");
            }
        }

        for (const entry of this.#toc) {            
            crawl(entry, "/");
        }

        //console.log(this.#toc)
    }

    /**
     * Gets a list of files/folders in the path
     */
    async #getListing(path) {
        await this.#loadToc();
        
        function find(list, tokens) {
            if (!tokens.length) return list.filter((entry) => entry.type == "dir");

            const first = tokens.shift();

            for (const entry of list) {
                if (entry.name != first || entry.type != "dir" || !entry.children) continue;
                return find(entry.children, tokens)
            }

            throw new Error("Example " + first + " not found");
        }

        return find(this.#toc, path ? path.split("/") : []);
    }

    /**
     * Creates the listing elements (TR)
     */
    #getListingElement(entry) {
        const that = this;

        return $('<tr/>').append(
            $('<td/>').append(
                // Listing entry icon
                $('<span class="fa"/>')
                .addClass(this.#entryIsExample(entry) ? 'fa-play' : 'fa-folder'),

                // Listing entry link
                $('<span class="listing-link" />')
                .text(entry.name)
                .on('click', async function() {
                    try {
                        that.#controller.routing.call(that.#getExampleUrl(entry.path))
                    } catch (e) {
                        that.#controller.handle(e);
                    }
                })
            )
        )
    }

    /**
     * Returns if the passed entry contains an example
     */
    #entryIsExample(entry) {
        if (entry.type != "dir") return false;

        for (const child of entry.children || []) {
            if (child.type == "dir") return false;
        }
        
        return true;
    }

    /**
     * Returns a href for the passed path
     */
    #getExampleUrl(path) {
        return encodeURI("example" + path);
    }
}