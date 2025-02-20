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

    select() {
        this.#tabs.setActive(this);
    }

    deactivate() {
        if (!this.header) return;
        this.header.removeClass("active");
        this.container.hide();
    }

    activate() {
        if (!this.header) return;
        this.header.addClass("active");
        this.container.show();
    }
}