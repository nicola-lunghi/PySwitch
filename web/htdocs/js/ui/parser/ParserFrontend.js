/**
 * Parser frontend (shows all actions etc.)
 */
class ParserFrontend {

    inputs = [];   // Array of parser frontends
    parser = null;
    check = null;

    #controller = null;
    #toUpdate = [];    // Queue for parser frontends which had changes recently.

    constructor(controller, parser) {
        this.#controller = controller;
        this.parser = parser;

        this.check = new ParserFrontendChecks(this);
    }

    async destroy() {
        for(const f of this.inputs) {
            await f.destroy();
        }
    }

    /**
     * Adds a new frontend for an input
     */
    async addInput(model, inputElement) {
        if (!inputElement) return;

        const input = await this.parser.input(model.port);
        
        this.inputs.push(
            new ParserFrontendInput(this.#controller, this, input, inputElement)
        );
    }

    /**
     * Must be called after all inputs have been added
     */
    async init() {
        await this.check.process();

        for(const f of this.inputs) {
            await f.init();
        }
    }

    /**
     * Schedules an input frontend for updating the config
     */
    scheduleForUpdate(input) {
        if (this.#toUpdate.includes(input)) return;

        this.#toUpdate.push(input);
    }

    /**
     * Update the data model from the input frontends in the queue. Includes exception handling
     * as this is eventually called without await.
     */
    async updateConfig() {
        try {
            await this.#doUpdateConfig();

        } catch (e) {
            this.#controller.handle(e);
        }
    }

    /**
     * Implementation for updateConfig
     */
    async #doUpdateConfig() {
        while (this.#toUpdate.length > 0) {
            const inputToUpdate = this.#toUpdate.shift();
            await inputToUpdate.updateInput();
        }

        // All set_actions calls have suppressed updating until now, so we need to do this here
        this.parser.updateConfig();

        // Restart the emulated controller
        await this.#controller.restart("none");
    }
}