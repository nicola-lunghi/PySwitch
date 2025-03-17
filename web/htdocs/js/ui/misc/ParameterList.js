class ParameterList {

    controller = null;
    onCommit = null;

    constructor(controller, onCommit) {
        this.controller = controller;
        this.onCommit = onCommit;
    }

    /**
     * Generate the DOM for the properties panel, or null if no options are present.
     */
    async get() {
        const options = await this.getOptions();
        if (!options) return null;

        const headline = await this.getHeadline();

        const that = this;
        return $('<span class="parameter-list-container" />').append(
            $('<div class="parameter-list" />').append(
                !headline ? null :
                $('<div class="parameter-comment" />')
                .html(headline),

                $('<div class="parameters" />').append(
                    $('<table />').append(
                        $('<tbody />').append(
                            options
                        )
                    )
                )
            ),

            // Commit button
            $('<div class="buttons" />').append(
                $('<div class="button" />')
                .text("Done")
                .on('click', async function() {
                    try {
                        await that.onCommit();
    
                    } catch(e) {
                        that.controller.handle(e);
                    }
                })
            )
        )
    }

    /**
     * Can return a headline
     */
    async getHeadline() {
        return null;
    }

    /**
     * Must return the option table rows (array of TR elements) or null if no options are available.
     */
    async getOptions() {
        throw new Error("Must be implemented in child classes");
    }
    
    ///////////////////////////////////////////////////////////////////////////////////////

    /**
     * Returns the passed element with the passed comment on hover
     */
    withComment(el, comment) {
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

    /**
     * Creates a boolean input row
     */
    createBooleanInputRow(name, comment, value, onChange) {
        const that = this;
        return this.withComment(
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
                            that.controller.handle(e);
                        }
                    })
                    .prop('checked', value)
                )
            ),
            comment
        )
    }

    /**
     * Creates a numeric input row
     */
    createNumericInputRow(name, comment, value, onChange) {
        const that = this;
        return this.withComment(
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
                            that.controller.handle(e);
                        }
                    })
                    .val(value)
                )
            ),
            comment
        )
    }
}