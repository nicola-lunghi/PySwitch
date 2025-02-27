class ParserChecks {

    #messages = null;
    #usages = null;

    #parser = null;

    constructor(parser) {
        this.#parser = parser;
        this.reset();
    }

    /**
     * Reset messages buffer
     */
    reset() {
        this.#messages = [];
        this.#usages = new Map();
    }

    /**
     * Process all checks (buffered)
     */
    async messages() {
        if (this.#messages.length > 0) return this.#messages;

        await this.#checkDisplayLabels();

        return this.#messages;
    }

    /**
     * Returns messages related to an action
     * 
     * @param {*} action 
     * @returns 
     *
    async messagesForAction(action) {
        const messages = await this.messages();

        const ret = [];

        for (const msg of messages) {
            for (const a of msg.actions) {
                if (a.name == action.name && a.client == action.client) {
                    ret.push(msg);
                }
            }
        }

        return ret;
    }

    /**
     * Returns an array of usages containing the display as an argument (buffered)
     */
    async getDisplayUsages(displayName) {
        if (this.#usages.has(displayName)) return this.#usages.get(displayName);

        /**
         * Returns an array of actions containing the display as an argument
         */
        async function getContainedDisplays(input, hold) {
            const actions = await input.actions(hold);

            const ret = [];
            for (const action of actions) {
                for (const arg of JSON.parse(action.arguments())) {                
                    if (arg.value == displayName) {
                        ret.push({
                            input, input,
                            name: action.name,
                            client: action.client,
                            display: displayName
                        });
                    }                                        
                }
            }
            return ret;
        }

        // Crawl all actions for parameters with the display
        const hw = await this.#parser.getHardwareInfo();
        
        let usages = [];
        for (const inputDescr of hw) {
            const input = await this.#parser.input(inputDescr.data.model.port);

            const contained = await getContainedDisplays(input, false);
            const containedHold = await getContainedDisplays(input, true);

            usages = usages.concat(contained, containedHold);
        }

        this.#usages.set(displayName, usages);

        return usages;        
    }

    /**
     * Check for multiple assignments of DisplayLabels
     */
    async #checkDisplayLabels() {
        const displays = await this.#parser.getAvailableDisplays();

        // Crawl all actions for parameters with the displays
        for (const display of displays) {
            const usages = await this.getDisplayUsages(display);

            if (usages.length > 1) {
                this.#messages.push({
                    type: "W",
                    message: "DisplayLabel " + display + " is used more than once. This leads to unpredicted behaviour on the label.",
                    parameter: display,
                    actions: usages
                })    
            }
        }
    }
}