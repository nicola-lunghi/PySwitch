/**
 * Parser frontend (shows all actions etc.)
 */
class ParserFrontend {

    inputs = [];   // Array of parser frontends
    parser = null;

    #controller = null;
    #toUpdate = [];    // Queue for parser frontends which had changes recently.

    constructor(controller, parser) {
        this.#controller = controller;
        this.parser = parser;
    }

    async destroy() {
        for(const f of this.inputs) {
            await f.destroy();
        }
    }

    /**
     * Adds a new frontend for an input
     */
    async addInput(port, inputElement) {
        if (!inputElement) return;

        const input = await this.parser.input(port);
        
        this.inputs.push(
            new ParserFrontendInput(this.#controller, this, input, inputElement)
        );
    }

    /**
     * Must be called after all inputs have been added
     */
    async init() {
        for(const f of this.inputs) {
            await f.init();
        }
    }

    /**
     * Schedules an input frontend for updating the Configuration
     */
    scheduleForUpdate(input) {
        if (this.#toUpdate.includes(input)) return;

        this.#toUpdate.push(input);
    }

    /**
     * Update the Configuration data from the input frontends. Includes exception handling
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
        await this.#controller.stop();

        while (this.#toUpdate.length > 0) {
            const inputToUpdate = this.#toUpdate.shift();
            await inputToUpdate.updateInput();
        }


        // Remove all inputs and LEDs etc.
        await this.#controller.ui.frontend.reset();

        // After the frontend reset, we must let some time pass for the UI to flush.
        const that = this;
        setTimeout(async function() {
            // All set_actions calls have suppressed updating until now, so we need to do this here
            that.parser.updateConfig();

            // Restart the emulated controller
            await that.#controller.restart("none");
        }, 10)
    }
}