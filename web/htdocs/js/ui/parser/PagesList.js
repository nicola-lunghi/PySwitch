class PagesList {

    #pages = [];

    /**
     * Returns the DOM for the pages list
     */
    async get() {
        return $('<span class="pages-list-container" />')
    }

    /**
     * Sets the list from the passed pages list
     */
    set(value) {
        // console.log(value);
        this.#pages = value;
    }

    /**
     * Returns the pages list value
     */
    value() {
        return this.#pages;
    }
}