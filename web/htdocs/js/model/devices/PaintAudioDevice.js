class PaintAudioDevice extends Device {

    #filename = null;

    constructor(filename) {
        super();
        this.#filename = filename;
    }

    /**
     * Returns the hardware definition script file name in the lib/pyswitch/hardware/devices/ folder
     */
    getHardwareImportPath() {
        return "pyswitch.hardware.devices." + this.#filename
    }

    /**
     * Returns the class(es) to set on the device element
     */
    getDeviceClass() {
        switch (this.#filename) {
            case 'pa_midicaptain_nano_4':
                return "midicaptain midicaptain-nano-4";

            case 'pa_midicaptain_mini_6':
                return "midicaptain midicaptain-mini-6";

            case 'pa_midicaptain_10':
                return "midicaptain midicaptain-10";
        }

        throw new Error("Unknown device file: " + this.#filename);
    }
}