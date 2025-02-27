/**
 * Represents one tab
 */
class Tab {

    name = null;
    container = null;
    header = null;

    #tabs = null;

    constructor(container, name) {
        this.container = container;
        this.name = name;
    }

    /**
     * Must be called before usage
     */
    init(tabs) {
        this.#tabs = tabs;
    }

    /**
     * Destroy the tab
     */
    destroy() {
        this.container.remove();
        
        if (this.header) {
            this.header.remove()
        }
    }

    /**
     * Refresh tab if needed
     */
    refresh() {
    }
    
    /**
     * Generates the header element
     */
    getHeader() {
        if (this.header) return this.header;

        const that = this;
        this.header = $('<span class="header-item" />')
            .text(this.name)
            .on('click', async function() {
                try {
                    that.select();

                } catch (e) {
                    console.error(e);
                }

            })

        return this.header;
    }

    /**
     * Generates custom buttons for the tab, if any
     */
    getButtons() {
        return null;
    }

    /**
     * If dirty, asks the user to confirm the action he wants to take.
     */
    confirmIfDirty() {
        return true;
    }

    /**
     * Select the tab
     */
    select() {
        this.#tabs.setActive(this);
    }

    /**
     * Deactivate the tab (not selected)
     */
    deactivate() {
        if (this.header) {
            this.header.removeClass("active");
        }
        
        this.container.hide();
    }

    /**
     * Activate the tab (selected)
     */
    activate() {
        if (this.header) {
            this.header.addClass("active");
        }
        
        this.container.show();
    }

    /**
     * Remove the tab
     */
    remove() {
        this.#tabs.remove(this);
    }
}