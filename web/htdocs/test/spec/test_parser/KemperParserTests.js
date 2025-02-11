class KemperParserTests {

    pyswitch = null;

    constructor() {
        this.pyswitch = new PySwitchRunner(
            {
                domNamespace: "pyswitch",
                updateIntervalMillis: 10
            }, 
            "test-pyswitch-example"
        );
    }

    async process() {
        await this.pyswitch.init("../");

        const config = new WebConfiguration("data/test-presets/change-action");

        // Create and init parser
        const parser = await config.parser(this.pyswitch);
        expect(parser).toBeInstanceOf(KemperParser);

        // Parse the code
        const tree = await parser.parse();

        // TODO do modifications

        // Unparse again
        const unparsed = await parser.unparse();

        console.log(unparsed.inputs_py);

        // // Check if the result is the same as before
        // const data = await config.get();
        // expect(unparsed.inputs_py).toEqual(data.inputs_py);
        // expect(unparsed.display_py).toEqual(data.display_py);
    }
}