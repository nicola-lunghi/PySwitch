/**
 * Implements the parameter editor
 */
class InputSettings {
    
    #definition = null;
    #input = null;
    #controller = null;

    // #advancedRows = null;
    // #advancedLevel = 0;

    constructor(controller, definition, input) {
        this.#controller = controller;
        this.#definition = definition;
        this.#input = input;
    }

    /**
     * Generate the DOM for the properties panel
     */
    async get() {
        const that = this;
        // this.#advancedRows = [];

        /**
         * Returns the passed element with the passed comment on hover
         */
        function withComment(el, comment) {
            if (comment) {
                tippy(el[0], {
                    content: comment,
                    theme: "actionparameter",
                    placement: "left",
                    duration: 0
                });
            }

            return el;
        }

        function getBooleanInput(name, comment, value, onChange) {
            return withComment(
                $('<tr />').append(                            
                    $('<td />').append(
                        $('<span />').text(name)
                    ),

                    // Input
                    $('<td />').append(
                        $('<input type="checkbox" />')
                        .on('change', async function() {
                            try {
                                await onChange(!!$(this).prop('checked'))
                            
                            } catch (e) {
                                that.#controller.handle(e);
                            }
                        })
                        .prop('checked', value)
                    )
                ),
                comment
            )
        }

        function getNumericInput(name, comment, value, onChange) {
            return withComment(
                $('<tr />').append(                            
                    $('<td />').append(
                        $('<span />').text(name)
                    ),

                    // Input
                    $('<td />').append(
                        $('<input type="number" />')
                        .on('change', async function() {
                            try {
                                await onChange($(this).val())
                            
                            } catch (e) {
                                that.#controller.handle(e);
                            }
                        })
                        .val(value)
                    )
                ),
                comment
            )
        }
        
        function getSwitchOptions() {
            return [
                getBooleanInput(
                    "Hold Repeat",
                    "This option keeps repeating the hold actions again and again as long as the switch is held.",
                    that.#input ? that.#input.hold_repeat() : false,
                    async function(value) {
                        that.#input.set_hold_repeat(value);

                        await that.#controller.restart({
                            message: "none"
                        });
                    }
                ),
                getNumericInput(
                    "Hold Time", 
                    "Amount of time you have to press the switch for the hold actions to be triggered (Milliseconds).",
                    that.#input ? that.#input.hold_time_millis() : 0,
                    async function(value) {
                        that.#input.set_hold_time_millis(value);

                        await that.#controller.restart({
                            message: "none"
                        });
                    }
                )
            ]
        }

        function getOptions() {
            switch (that.#definition.data.model.type) {
                case "AdafruitSwitch": return getSwitchOptions();
            }
            return null;
        }

        const options = getOptions();
        if (!options) return null;

        const ret = $('<div class="input-settings" />').append(
            $('<div class="input-comment" />')
            .html("These options apply to all actions of " + this.#definition.displayName + ":"),

            $('<div class="input-parameters" />').append(
                $('<table />').append(
                    $('<tbody />').append(
                        options
                    )
                )
            )
        );

        return ret;
    }
}