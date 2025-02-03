class WebConfiguration extends Configuration {

    #path = null;
    #title = null;

    constructor(path, title = null) {
        super(decodeURI(path));
        this.#path = path;
        this.#title = title;

        if (!this.#title) {
            const splt = this.name.split("/");
            this.#title = splt.pop();
        }
    }

    /**
     * Returns the text for the head line
     */
    async headline() {
        return this.#title;
    }

    /**
     * Loads config files from the web.
     */
    async load() {
        return {
            inputs_py: await Tools.fetch(this.#path + "/inputs.py"),
            display_py: await Tools.fetch(this.#path + "/display.py")
        }
    }
}