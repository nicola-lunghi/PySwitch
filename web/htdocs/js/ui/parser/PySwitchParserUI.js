class PySwitchParserUI {

    #controller = null;
    
    constructor(controller) {
        this.#controller = controller;
    }

    /**
     * Generates the UI according to the given Configuration instance
     */
    async apply(parser) {
        // Add the parser frontend to all inputs
        const inputContainer = $('#pyswitch-inputs');

        await inputContainer.children().each(async function() {
            const port = parseInt(this.dataset.port);
            
            const definition = await parser.getInputActions(port);
            
            const actions = definition.actions.map((item) =>
                $('<span class="button actions" data-toggle="tooltip" title="Action on normal press" />')
                .text(item.name)
            );

            const actionsHold = definition.actionsHold.map((item) =>
                $('<span class="button actions-hold" data-toggle="tooltip" title="Action on long press" />')
                .text(item.name)
            );

            $(this).append(
                $('<div class="pyswitch-parser-frontend"  />').append(
                    actions,
                    actionsHold
                )
            )
        });

        // this.#container.empty();
        // this.#inputs = [];
        
        // // Get switch data models
        // const models = await parser.inputs();

        // // Create user interfaces for each model
        // for (const model of models) {
        //     const inputUi = new KemperParserInputUI(model);
        //     this.#inputs.push(inputUi);

        //     this.#container.append(await inputUi.dom());
        // }
    }
}