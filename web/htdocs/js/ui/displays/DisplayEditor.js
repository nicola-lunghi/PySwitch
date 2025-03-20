/**
 * Implements the display editor
 */
class DisplayEditor extends ParameterList {
    
    #displayCanvas = null;
    #mirrorCanvas = null;

    constructor(controller, displayCanvas, onCommit) {
        super(controller, onCommit);
        this.#displayCanvas = displayCanvas;
    }

    /**
     * Start updates for the mirror canvas
     */
    init() {
        this.#updateCanvas();        
    }

    /**
     * Must return the option table rows (array of TR elements) or null if no options are available.
     */
    async getOptions() {
        this.#mirrorCanvas = $('<canvas />');
        
        return [
            this.createNumericInputRow(
                "Number of Header Displays",
                "Number of displays sharing the area above the rig name",
                2,
                async function(value) {
                    // that.#input.setHoldRepeat(value);

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
                    // that.#input.setHoldRepeat(value);

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
                    // that.#input.setHoldRepeat(value);

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
                    // that.#input.setHoldRepeat(value);

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
                    // that.#input.setHoldRepeat(value);

                    // await that.controller.restart({
                    //     message: "none"
                    // });
                }
            ),

            // this.createSelectInputRow(
            //     "Tuner Display",
            //     "If set, and the corresponding client goes into tuner mode, the controller will show a tuner, too",
            //     [
            //         "Kemper: Tuner Display TODO"
            //     ],
            //     "foo",
            //     async function(value) {
            //         // that.#input.setHoldRepeat(value);

            //         // await that.controller.restart({
            //         //     message: "none"
            //         // });
            //     }
            // ),

            $('<tr />'). append(
                $('<td colspan="2" class="canvas-container" />').append(
                    this.#mirrorCanvas
                )
            )
        ]
    }

    /**
     * The canvas is updated periodically
     */
    #updateCanvas() {
        // If the mirror canvas is attached to the DOM, schedule the next update
        if (document.contains(this.#mirrorCanvas[0])) {
            const that = this;

            setTimeout(function() {
                that.#updateCanvas();
            }, 100);
        }

        // Mirror the pyswitch canvas to a local one
        const context = this.#mirrorCanvas[0].getContext('2d');    
        
        this.#mirrorCanvas[0].width = this.#displayCanvas[0].width;
        this.#mirrorCanvas[0].height = this.#displayCanvas[0].height;
    
        context.drawImage(this.#displayCanvas[0], 0, 0);
    }
}