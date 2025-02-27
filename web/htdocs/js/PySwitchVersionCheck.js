class PySwitchVersionCheck {

    #controller = null;

    constructor(controller) {
        this.#controller = controller;
    }

    /**
     * Compares the PySwitch versions of the controller and the emulator
     */
    async check() {
        console.log("Check PySwitch version on remote controller")

        const controllerMisc = await this.#controller.device.loadFile("/lib/pyswitch/misc.py", true);
        const emulatorMisc = await Tools.fetch("circuitpy/lib/pyswitch/misc.py");

        if (controllerMisc != emulatorMisc) {
            this.#controller.ui.notifications.message("The PySwitch version on the controller does not match the verison of the Emulator. Please update your controller or use an appropriate version of the Emulator instead.", "W");
        } else {
            console.log(" -> PySwitch versions matching OK")
        }
    }

}