class ExampleEntry {

    #browser = null;

    name = null;
    path = null;
    type = null;
    children = [];

    constructor(browser, name, path, type, parent = null) {
        this.name = name;
        this.path = path;
        this.type = type;
        this.parent = parent;
        this.#browser = browser;
    }

    /**
     * Creates the listing elements (TR)
     */
    getElement() {
        const that = this;

        return $('<tr/>').append(
            $('<td/>').append(
                // Listing entry icon
                $('<span class="fa"/>')
                .addClass(this.isExample() ? 'fa-play' : 'fa-folder'),

                // Listing entry link
                $('<span class="listing-link" />')
                .text(this.name)
                .on('click', async function() {
                    try {
                        await that.#browser.browse(that);

                    } catch (e) {
                        that.#browser.controller.handle(e);
                    }
                })
            )
        )
    }

    /**
     * Returns if the entry contains an example
     */
    isExample() {
        if (this.type != "dir") return false;

        for (const child of this.children) {
            if (child.type == "dir") return false;
        }
        
        return true;
    }

    /**
     * Returns a href for the passed path
     */
    getUrl() {
        return encodeURI("example" + this.path);
    }

}