/**
 * Base class for controller devices
 */
class Device {

    /**
     * Returns the device handler from the passed Configuration instance
     */
    static async getInstance(config) {
        const data = await config.get();

        if (data.inputs_py.includes("pyswitch.hardware.devices.pa_midicaptain_nano_4")) {
            return new PaintAudioDevice('pa_midicaptain_nano_4')
        }
        if (data.inputs_py.includes("pyswitch.hardware.devices.pa_midicaptain_mini_6")) {
            return new PaintAudioDevice('pa_midicaptain_mini_6')
        }
        if (data.inputs_py.includes("pyswitch.hardware.devices.pa_midicaptain_10")) {
            return new PaintAudioDevice('pa_midicaptain_10')
        }
        
        throw new Error("Unknown device type");
    }

    /**
     * Returns the hardware definition script file name in the lib/pyswitch/hardware/devices/ folder
     */
    getHardwareImportPath() {
        throw new Error("Implement this in child classes");
    }

    /**
     * Returns the class(es) to set on the device element
     */
    getDeviceClass() {
        throw new Error("Implement this in child classes");
    }
}