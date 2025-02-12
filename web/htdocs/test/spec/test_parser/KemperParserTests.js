class KemperParserTests {

    pyswitch = null;    // Shared runner

    /**
     * Must be called before any of the tests run
     */
    async #init() {
        if (this.pyswitch) return;

        this.pyswitch = new PySwitchRunner(
            {
                domNamespace: "pyswitch",
                updateIntervalMillis: 10
            }, 
            "test-pyswitch-example"
        );

        await this.pyswitch.init("../");
    }

    // async process() {
        // await this.#init();

        // const config = new WebConfiguration("data/test-presets/change-action");

        // // Create and init parser
        // const parser = await config.parser(this.pyswitch);
        // expect(parser).toBeInstanceOf(KemperParser);

        // // Parse the code
        // const tree = await parser.parse();

        // // TODO do modifications

        // // Unparse again
        // const unparsed = await parser.unparse();

        // console.log(unparsed.inputs_py);

        // // Check if the result is the same as before
        // const data = await config.get();
        // expect(unparsed.inputs_py).toEqual(data.inputs_py);
        // expect(unparsed.display_py).toEqual(data.display_py);
    // }

    async getInputActionsDefault() {
        await this.#init();
        const config = new WebConfiguration("data/test-presets/get-inputs-default");

        const parser = await config.parser(this.pyswitch);
        expect(parser).toBeInstanceOf(KemperParser);
        
        expect(await parser.getInputActions(1)).toEqual({ actionsHold: [], actions: [{ name: "RIG_UP" }] });
        expect(await parser.getInputActions(9)).toEqual({ actionsHold: [], actions: [{ name: "RIG_DOWN" }] });
        expect(await parser.getInputActions(25)).toEqual({ actionsHold: [], actions: [{ name: "BANK_UP" }] });
        expect(await parser.getInputActions(10)).toEqual({ actionsHold: [], actions: [{ name: "BANK_DOWN" }] });
    }

    async getInputActionsHold() {
        await this.#init();
        const config = new WebConfiguration("data/test-presets/get-inputs-hold");

        const parser = await config.parser(this.pyswitch);
        expect(parser).toBeInstanceOf(KemperParser);

        expect(await parser.getInputActions(1)).toEqual({ actionsHold: [], actions: [{ name: "RIG_UP" }] });
        expect(await parser.getInputActions(9)).toEqual({ actionsHold: [], actions: [{ name: "RIG_DOWN" }] });
        expect(await parser.getInputActions(25)).toEqual({ actionsHold: [{ name: "TUNER_MODE" }], actions: [{ name: "BANK_UP" }] });
        expect(await parser.getInputActions(10)).toEqual({ actionsHold: [], actions: [{ name: "BANK_DOWN" }] });
    }
}