class PySwitchParserUI {

    #controller = null;
    
    constructor(controller) {
        this.#controller = controller;
    }

    /**
     * Generates the UI according to the given Configuration instance
     */
    async apply(parser) {
        // Add a parser frontend to all inputs
        const inputContainer = $('#pyswitch-inputs');

        await inputContainer.children().each(async function() {
            const port = parseInt(this.dataset.port);
            
            const input = await parser.input(port);
            const actions = await input.actions();
            const actionsHold = await input.actions(true);
            
            const actionsElements = actions.map((item) =>
                $('<span class="button actions" data-toggle="tooltip" title="Action on normal press" />')
                .text(item.name)
            );

            const actionsHoldElements = actionsHold.map((item) =>
                $('<span class="button actions-hold" data-toggle="tooltip" title="Action on long press" />')
                .text(item.name)
            );

            $(this).append(
                $('<div class="pyswitch-parser-frontend"  />').append(
                    actionsElements,
                    actionsHoldElements
                )
            )
        });
    }
}