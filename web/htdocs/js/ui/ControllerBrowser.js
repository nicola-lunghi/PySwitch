class ControllerBrowser {

    #element = null;
    #controller = null;
    
    constructor(controller, element) {
        this.#controller = controller;
        this.#element = element;
    }

    #build(items, headline) {
        this.#element.empty();

        const that = this;
        this.#element.append(
            // Headline
            $('<div class="headline"/>')
            .text(headline),

            // Listing
            $('<table/>').append(
                $('<tbody/>').append(items)
            ),

            // Close button
            $('<span class="fa fa-times close-button"/>')
            .on('click', async function() {
                that.hide();
            })
        );
    }

    /**
     * Show the browser. 
     * onSelect(portName) => void
     */
    async browse(headline, onSelect) {
        this.#controller.ui.block();
        
        const listing = await this.#controller.device.bridge.getMatchingPortPairs();
        
        const items = [];
        for(const entry of listing) {
            items.push(this.#getListingElement(entry, onSelect));
        }

        this.#build(items, headline);

        this.show();
    }

    hide() {
        this.#controller.ui.progress(1);
        this.#element.hide();
    }

    show() {        
        this.#element.show();
    }

    /**
     * Creates the listing elements (TR)
     */
    #getListingElement(entry, onSelect) {
        const that = this;

        return $('<tr/>').append(
            $('<td/>').append(
                // Listing entry icon
                $('<span class="fa"/>')
                .addClass('fa-device'),

                // Listing entry link
                $('<span class="listing-link" />')
                .text(entry.input.name)
                .on('click', async function() {
                    try {
                        //that.#controller.routing.call(that.#getExampleUrl(entry.path))
                        await onSelect(entry.input.name);

                    } catch (e) {
                        that.#controller.handle(e);
                    }
                })
            )
        )
    }
}