// class KemperHardware {

//     #parser = null;
// TODO delete file
//     constructor(parser) {
//         this.#parser = parser;
//     }
//     /**
//      * Returns an array containing all inputs, represented by KemperParserInput instances, which
//      * are possible on the device the config targets on.
//      */
//     async get() {
//         const importPath = await this.#getHardwareImportPath();

//         const hardwareJson = await this.#parser.runner.pyodide.runPython(`
//             from PySwitchHardware import PySwitchHardware
//             pySwitchHardware = PySwitchHardware()
//             pySwitchHardware.get("` + importPath + `")
//         `);
//         return JSON.parse(hardwareJson);
//     }

//     ///////////////////////////////////////////////////////////////////////////////////////////////////////////////

//     /**
//      * Returns the hardware definition script file name in the lib/pyswitch/hardware/devices/ folder
//      */
//     async #getHardwareImportPath() {
//         switch (await this.#parser.getDeviceType()) {
//             case KemperParser.DEVICE_TYPE_NANO_4:
//                 return "pyswitch.hardware.devices.pa_midicaptain_nano_4"

//             case KemperParser.DEVICE_TYPE_MINI_6:
//                 return "pyswitch.hardware.devices.pa_midicaptain_mini_6"

//             case KemperParser.DEVICE_TYPE_10:
//                 return "pyswitch.hardware.devices.pa_midicaptain_10"
//         }
//     }
// }