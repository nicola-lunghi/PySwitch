class ParserFrontendChecks {

    messages = [];

    #frontend = null;

    constructor(frontend) {
        this.#frontend = frontend;
    }

    /**
     * Process all checks
     */
    async process() {
        this.messages = [];

        await this.#checkDisplayLabels();
    }

    /**
     * Check for multiple assignments of DisplayLabels
     */
    async #checkDisplayLabels() {
        const displays = await this.#frontend.parser.getAvailableDisplays();

        /**
         * Returns an array of actions containing the display as an argument
         */
        async function getContainedDisplays(input, displayName, hold) {
            const actions = await input.actions(hold);

            const ret = [];
            for (const action of actions) {
                for (const arg of JSON.parse(action.arguments())) {                
                    if (arg.value == displayName) {
                        ret.push({
                            name: action.name,
                            client: action.client
                        });
                    }                                        
                }
            }
            return ret;
        }

        // Crawl all actions for parameters with the displays
        for (const display of displays) {
            let usages = [];
            for (const input of this.#frontend.inputs) {
                const contained = await getContainedDisplays(input.input, display, false);
                const containedHold = await getContainedDisplays(input.input, display, true);

                usages = usages.concat(contained, containedHold);
            }

            if (usages.length > 1) {
                this.messages.push({
                    type: "W",
                    message: "DisplayLabel " + display + " is used more than once. This leads to unpredicted behaviour on the label.",
                    display: display,
                    actions: usages
                })    
            }
        }
    }
}