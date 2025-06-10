/**
 * Implements the input options for the display editor
 */
class DisplayEditorParameters extends ParameterList {
    
    // #definition = null;
    // #input = null;

    // constructor(controller, definition) {
    //     super(controller)
    //     this.#definition = definition;
    // }

    // /**
    //  * Must return the headline
    //  */
    // async getHeadline() {
    //     return "These options apply to all actions of " + this.#definition.displayName + ":"
    // }

    /**
     * Must return the option table rows (array of TR elements) or null if no options are available.
     */
    async getOptions() {
        const that = this;
        // function getSwitchOptions() {
        //     return [
        //         that.createBooleanInputRow(
        //             "Hold Repeat",
        //             "This option keeps repeating the hold actions again and again as long as the switch is held.",
        //             that.#input ? that.#input.holdRepeat() : false,
        //             async function(value) {
        //                 that.#input.setHoldRepeat(value);

        //                 await that.controller.restart({
        //                     message: "none"
        //                 });
        //             }
        //         ),
                
        //         that.createNumericInputRow(
        //             "Hold Time", 
        //             "Amount of time you have to press the switch for the hold actions to be triggered (Milliseconds).",
        //             holdTimeMillis ? holdTimeMillis : 600,
        //             async function(value) {
        //                 that.#input.setHoldTimeMillis(value);

        //                 await that.controller.restart({
        //                     message: "none"
        //                 });
        //             }
        //         )
        //     ]
        // }

        // switch (this.#definition.data.model.type) {
        //     case "AdafruitSwitch": return getSwitchOptions();
        // }
        
        // No options available
        return null;
    }
}