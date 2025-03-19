/**
 * Implements the input options editor
 */
class InputSettings extends ParameterList {
    
    #definition = null;
    #input = null;

    constructor(controller, definition, input, onCommit) {
        super(controller, onCommit)
        this.#definition = definition;
        this.#input = input;
    }

    /**
     * Must return the headline
     */
    async getHeadline() {
        return "These options apply to all actions of " + this.#definition.displayName + ":"
    }

    /**
     * Must return the option table rows (array of TR elements) or null if no options are available.
     */
    async getOptions() {
        const that = this;

        function getSwitchOptions() {
            return [
                that.createBooleanInputRow(
                    "Hold Repeat",
                    "This option keeps repeating the hold actions again and again as long as the switch is held.",
                    that.#input ? that.#input.holdRepeat() : false,
                    async function(value) {
                        that.#input.setHoldRepeat(value);

                        await that.controller.restart({
                            message: "none"
                        });
                    }
                ),
                
                that.createNumericInputRow(
                    "Hold Time", 
                    "Amount of time you have to press the switch for the hold actions to be triggered (Milliseconds).",
                    that.#input ? that.#input.holdTimeMillis() : 0,
                    async function(value) {
                        that.#input.setHoldTimeMillis(value);

                        await that.controller.restart({
                            message: "none"
                        });
                    }
                )
            ]
        }

        switch (this.#definition.data.model.type) {
            case "AdafruitSwitch": return getSwitchOptions();
        }
        
        // No options available
        return null;
    }
}