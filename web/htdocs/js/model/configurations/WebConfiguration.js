class WebConfiguration extends Configuration {

    #path = null;

    constructor(path) {
        super(decodeURI(path));
        this.#path = path;
    }

    /**
     * Returns the text for the head line
     */
    async headline() {
        const splt = this.name.split("/");
        return splt.pop();
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