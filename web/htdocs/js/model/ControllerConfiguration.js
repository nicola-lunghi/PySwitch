class ControllerConfiguration extends Configuration {

    #controller = null;
    #portName = null;

    constructor(controller, portName) {
        super(portName);

        this.#controller = controller;
        this.#portName = portName;
    }

    /**
     * Loads config files from a PyMidiBridge enabled controller.
     */
    async load() {
        // Connect if not yet done
        await this.#controller.device.connect(this.#portName);

        // Get config scripts from the controller
        this.inputs_py = await this.#controller.device.loadFile("/inputs.py");
        this.display_py = await this.#controller.device.loadFile("/display.py");
    }
}