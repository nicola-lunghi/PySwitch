class DummyConfiguration extends Configuration {

    constructor() {
        super("Dummy");
    }

    /**
     * Loads config files from the web.
     */
    async load() {
        this.inputs_py = "Inputs = {}";
        this.display_py = [
            "from pyswitch.ui.ui import DisplayElement",
            "from pyswitch.clients.kemper import TunerDisplayCallback",
            "Splashes = TunerDisplayCallback(splash_default = DisplayElement())"
        ].join("\n");
    }
}