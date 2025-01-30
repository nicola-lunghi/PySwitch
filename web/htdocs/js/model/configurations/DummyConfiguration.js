class DummyConfiguration extends Configuration {

    constructor() {
        super("Dummy");
    }

    /**
     * Some dummy code that just does not throw any errors.
     */
    async load() {
        return {
            inputs_py: "Inputs = {}",
            display_py: [
                "from pyswitch.ui.ui import DisplayElement",
                "from pyswitch.clients.kemper import TunerDisplayCallback",
                "Splashes = TunerDisplayCallback(splash_default = DisplayElement())"
            ].join("\n")
        }
    }
}