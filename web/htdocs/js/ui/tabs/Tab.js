class Tab {

    name = null;
    container = null;
    header = null;

    constructor(container, name) {
        this.container = container;
        this.name = name;
    }

    /**
     * Generates the header element
     */
    getHeader(name) {
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
        // TODO
    }

    deactivate() {
        if (!this.header) return;
        this.header.removeClass("active");
    }

    activate() {
        if (!this.header) return;
        this.header.addClass("active");
    }
}