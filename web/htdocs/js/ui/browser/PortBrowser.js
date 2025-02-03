class PortBrowser extends BrowserBase {

    #build(items, headline) {
        this.element.empty();

        const that = this;
        this.element.append(
            $('<div class="content" />').append(
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
            )
        );
    }

    /**
     * Show the browser. 
     * onSelect(portName) => void
     */
    async browse(headline, onSelect, currentValue = null, additionalOptions = []) {
        const listing = await this.controller.midi.getMatchingPortPairs();
        
        const items = [];
        for(const entry of listing) {
            items.push(
                this.#getListingElement(
                    entry.input.name, 
                    entry.input.name, 
                    onSelect,
                    currentValue == entry.input.name
                )
            );
        }

        for (const addOption of additionalOptions) {
            items.push(
                this.#getListingElement(
                    addOption.text, 
                    addOption.value, 
                    onSelect,
                    currentValue == addOption.value
                )
            );
        }

        this.#build(items, headline);

        this.show();
    }

    /**
     * Creates the listing elements (TR)
     */
    #getListingElement(text, value, onSelect, isSelected) {
        const that = this;

        return $('<tr/>').append(
            $('<td/>').append(
                // Listing entry icon
                $('<span />')
                .addClass(isSelected ? 'fa fa-check' : ''),

                // Listing entry link
                $('<span class="listing-link" />')
                .text(text)
                .on('click', async function() {
                    try {
                        //that.#controller.routing.call(that.#getExampleUrl(entry.path))
                        await onSelect(value);

                        that.hide();

                    } catch (e) {
                        that.controller.handle(e);
                    }
                })
            )
        )
    }
}