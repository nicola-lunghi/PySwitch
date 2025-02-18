class ActionParserTests {

    pyswitch = null;    // Shared python runner

    async getAvailableActions() {
        await this.#init();
        const config = new MockConfiguration("", "");
        
        const parser = await config.parser(this.pyswitch);

        function download(data) {
            const dataString = JSON.stringify(data);
			const dataBlob = new Blob([dataString], {type: 'text/plain'});
			const url = URL.createObjectURL(dataBlob);
			
			window.saveAs(url, 'actions.json');
        }

        const basePath = "../";
        let actions = null;
        try {
            // Try to load. If not possible, generate the list and fail the test.
            actions = await parser.getAvailableActions(basePath);

            const current_actions = await parser.generateAvailableActions(basePath);

            if (JSON.stringify(current_actions) != JSON.stringify(actions)) {
                download(current_actions);

                console.error("This failure is intentional: The actions definition file is outdated. Please store the downloaded file at web/htdocs/definitions.");
                expect(3).toBe(4);
            } else {
                expect(1).toBe(1);
            }

        } catch (e) {
            console.error(e);

            // Generate and show
            actions = await parser.generateAvailableActions(basePath);
            download(actions);

            console.error("This failure is intentional: You dont have an actions list file prepared already. Please store the downloaded file at web/htdocs/definitions.");
            expect(1).toBe(2);
        }
    }

    /**
     * Must be called before any of the tests can be run
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
}