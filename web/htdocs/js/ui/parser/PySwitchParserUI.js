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
            
            const actions = await parser.getInputActions(port);
            
            $(this).append(
                $('<div class="pyswitch-parser-frontend" />').append(
                    $('<span class="button" />')
                    .text(actions.length ? actions[0].name : "None")
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