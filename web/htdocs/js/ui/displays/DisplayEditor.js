/**
 * Implements the display editor
 */
class DisplayEditor extends ParameterList {
    
    #displayCanvas = null;

    constructor(controller, displayCanvas, onCommit) {
        super(controller, onCommit);

        this.#displayCanvas = displayCanvas;
    }

    /**
     * Must return the option table rows (array of TR elements) or null if no options are available.
     */
    async getOptions() {
        const that = this;
        const mirrorCanvas = $('<canvas />');

        function updateCanvas() {
            setTimeout(function() {
                updateCanvas();
            }, 100);

            const context = mirrorCanvas[0].getContext('2d');
        
            //set dimensions
            mirrorCanvas[0].width = that.#displayCanvas[0].width;
            mirrorCanvas[0].height = that.#displayCanvas[0].height;
        
            //apply the old canvas to the new one
            context.drawImage(that.#displayCanvas[0], 0, 0);

            console.log("upd")
        }

        updateCanvas();
        
        return [
            this.createNumericInputRow(
                "Number of Header Displays",
                "Number of displays sharing the area above the rig name",
                2,
                async function(value) {
                    // that.#input.set_hold_repeat(value);

                    // await that.controller.restart({
                    //     message: "none"
                    // });
                }
            ),

            this.createNumericInputRow(
                "Number of Header Rows",
                "Number of rows for showing the amount of displays selected for the header",
                1,
                async function(value) {
                    // that.#input.set_hold_repeat(value);

                    // await that.controller.restart({
                    //     message: "none"
                    // });
                }
            ),

            this.createNumericInputRow(
                "Number of Footer Displays",
                "Number of displays sharing the area below the rig name",
                2,
                async function(value) {
                    // that.#input.set_hold_repeat(value);

                    // await that.controller.restart({
                    //     message: "none"
                    // });
                }
            ),

            this.createNumericInputRow(
                "Number of Footer Rows",
                "Number of rows for showing the amount of displays selected for the footer",
                1,
                async function(value) {
                    // that.#input.set_hold_repeat(value);

                    // await that.controller.restart({
                    //     message: "none"
                    // });
                }
            ),

            this.createBooleanInputRow(
                "Rig Name: Show Rig ID",
                "Adds the rig ID to the rig name display",
                false,
                async function(value) {
                    // that.#input.set_hold_repeat(value);

                    // await that.controller.restart({
                    //     message: "none"
                    // });
                }
            ),

            $('<tr />'). append(
                $('<td colspan="2" class="canvas-container" />').append(
                    mirrorCanvas
                )
            )
        ]
    }
}