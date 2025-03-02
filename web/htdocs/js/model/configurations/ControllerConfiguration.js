/**
 * Configuration loaded from a connected controller (via JsMidiBridge)
 */
class ControllerConfiguration extends Configuration {

    #portName = null;

    constructor(controller, portName) {
        super(controller, portName);

        this.#portName = portName;
    }

    /**
     * Loads config files from a PyMidiBridge enabled controller.
     */
    async load() {
        // Connect if not yet done
        await this.controller.device.connect(this.#portName);

        // Get config scripts from the controller
        const data = {
            inputs_py: await this.controller.device.loadFile("/inputs.py"),
            display_py: await this.controller.device.loadFile("/display.py")
        };

        // // Also start a check that compares PySwitch versions of the controller and local
        // const that = this;
        // setTimeout(function() {
        //     new PySwitchVersionCheck(that.#controller).check();
        // }, 100);        

        return data;
    }

    /**
     * Can the config be saved?
     */
    canBeSaved() {
        return true;
    }
    
    /**
     * Save the data to the location of the configuration
     */
    async doSave() {
        await this.controller.device.saveConfig(this, this.#portName);
    }
}