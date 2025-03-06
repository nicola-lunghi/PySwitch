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
        this.#messages = null;
        this.#usages = new Map();
    }

    /**
     * Process checks
     */
    async process() {
        if (this.#messages != null) return;

        this.#messages = [];
        await this.#checkDisplayLabels();
    }

    /**
     * Process all checks (buffered)
     */
    async messages() {
        await this.process();
        return this.#messages;
    }

    /**
     * Returns if the action has any relevant messages of the given type
     */
    async messagesForAction(actionCallProxy, type = null) {
        await this.process();
        
        const ret = [];
        
        for (const msg of this.#messages) {
            if (type && (msg.type != type)) continue;

            for (const action of msg.actions || []) {
                if (action.id() == actionCallProxy.id()) ret.push(msg);
            }
        }
        return ret;
    }

    /**
     * Returns an array of usages containing the display as an argument (buffered)
     */
    async getDisplayUsages(displayId) {
        if (this.#usages.has(displayId)) return this.#usages.get(displayId);

        /**
         * Returns an array of actions containing the display as an argument
         */
        async function getContainedDisplays(input, hold) {
            if (!input) return [];
            
            const actions = await input.actions(hold).toJs();

            const ret = [];
            for (const action of actions || []) {
                const args = JSON.parse(action.arguments());

                for (const arg of args) {                
                    if (arg.value == displayId) {
                        ret.push(action);
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

        this.#usages.set(displayId, usages);

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
            const pages = [...new Set(usages.map((item) => item.page()))];
            
            for (const page of pages) {
                const usagesFiltered = usages.filter((item) => !item.page() || (item.page() == page));
            
                if (usagesFiltered.length > 1) {
                    this.#messages.push({
                        type: "W",
                        message: "DisplayLabel " + display + " is used more than once (paging regarded). This leads to unpredicted behaviour on the label.",
                        parameter: "display",
                        value: display,
                        actions: usagesFiltered
                    })    
                }    
            }
        }
    }
}