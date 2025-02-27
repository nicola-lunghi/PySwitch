/**
 * TOC entry for the browser popup
 */
class BrowserEntry {

    value = null;       // Value for selection
    text = null;        // Display text
    parent = null;      // Parent BrowserEntry
    children = [];      // Child BrowserEntry list
    data = null;        // Options (plus arbitrary application data if needed)

    #browser = null;
    

    /**
     * {
     *      value:       Entry value
     *      text:        Entry text (default: use value). Cal also be a function(entry) => string
     *      parent:      Reference to parent entry
     *      onSelect:    Optional onSelect(entry) => void
     *      sortString:  Optional string to use for sorting (if not set, the text or value is used, in this order)
     *      childLayout: Optional: Array of column definitions. If not specified, only one column with the listing link is generated. Entry format:
     *                   {
     *                      type:        "link", "typeIcon". If not set, get must be passed.
     *                      get:         callback(entry) => DOM Element, used if no (or an invalid) type is set
     *                   }
     * }
     */
    constructor(browser, data = {}) {
        this.#browser = browser;
        this.data = data;

        this.value = data.value;
        this.text = data.text;
        this.parent = data.parent;

        // These must be accessed by their direct attributes! (could have been changed from outside)
        data.value = null;
        data.text = null;
        data.parent = null;

        // Default layout
        if (!this.data.childLayout) {
            this.data.childLayout = [
                {
                    type: "typeIcon"
                },
                {
                    type: "link"
                }
            ]
        }
    }

    /**
     * Returns a path inside the hierarchy, as an array of DOM elements.
     */
    async getHierarchicalPath() {
        const that = this;

        return (
                this.parent 
            ? 
                (await this.parent.getHierarchicalPath()).concat([
                    $('<span/>')
                    .text("/")
                ]) 
            : 
                []
        ).concat(
            [
                $('<span class="path-link"/>')
                .text(await this.getText())
                .on("click", async function() {
                    try {
                        await that.#browser.browse(that);

                    } catch (e) {
                        console.error(e);
                    }
                })
            ]
        );
    }

    /**
     * Returns the sort string to be used to compare this entry to its siblings
     */
    async getSortString() {
        return this.data.sortString ? this.data.sortString : this.getText();
    }

    /**
     * Returns the text to show
     */
    async getText() {
        return (typeof this.text == "function") ? this.text(this) : (this.text ? this.text : this.value);
    }

    /**
     * Creates the listing elements (TR)
     */
    async getElement(layout) {
        const that = this;

        const tr = $('<tr/>');

        for(const col of layout) {
            const td = $('<td/>');
            tr.append(td);                

            switch (col.type) {
                case "link":
                    td.append(
                        // Listing entry link
                        $('<span class="listing-link" />')
                        .text(await this.getText())
                        .on('click', async function() {
                            try {
                                await that.#browser.browse(that);

                            } catch (e) {
                                console.error(e);
                            }
                        })
                    )
                    break;
                
                case "typeIcon":
                    td.append(
                        // Listing entry link
                        $('<span class="fa"/>')
                        .addClass(this.isCallable() ? "fa-play" : "fa-folder")
                    )
                    break;

                default:
                    td.append(
                        await col.get(this)
                    );
                    break;
            }
        }

        return tr;
    }

    /**
     * Is the entry callable?
     */
    isCallable() {
        return !!this.data.onSelect;
    }

    /**
     * Calls the entry
     */
    async call() {        
        await this.data.onSelect(this);
    }
}