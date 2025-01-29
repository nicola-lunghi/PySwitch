class WebConfiguration extends Configuration {

    #path = null;

    constructor(path) {
        super(decodeURI(path));
        
        this.#path = path;
    }

    /**
     * Returns the text for the head line
     */
    headline() {
        const splt = this.name.split("/");

        return splt.pop();
    }

    /**
     * Loads config files from the web.
     */
    async load() {
        this.inputs_py = await Tools.fetch(this.#path + "/inputs.py"); //await (await fetch(this.#path + "/inputs.py")).text();
        this.display_py = await Tools.fetch(this.#path + "/display.py"); //(await fetch(this.#path + "/display.py")).text();
    }
}