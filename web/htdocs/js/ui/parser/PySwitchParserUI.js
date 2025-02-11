class PySwitchParserUI {

    #controller = null;
    
    // #inputs = null;

    constructor(controller) {
        this.#controller = controller;
    }

    /**
     * Regenerates the UI according to the given Configuration instance
     */
    async apply(parser) {
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