class PySwitchFrontend {

    #options = null;
    #container = null;

    constructor(container, options) {
        this.#container = container;
        this.#options = options;
    }

    /**
     * Initialize to a given set of inputs and splashes
     */
    async apply(parser) {
        const device = await parser.device();
        this.#container[0].className = device.getDeviceClass();

        // Clear contents and create container
        this.#container.empty();
        
        this.#container.append(
            $('<img id="' + this.#options.domNamespace + '-background" />'),
            $('<canvas id="' + this.#options.domNamespace + '-display" />')
        );

        // Add switches and LEDs
        await this.#initSwitches(parser);
    }

    /**
     * Creates DOM elements for all switches and LEDs. Expects the Inputs list from inputs.py.
     */
    async #initSwitches(parser) {
        const hw = await parser.getHardwareInfo();
        
        // Create container for all inputs
        const inputsContainer = $('<div id="' + this.#options.domNamespace + '-inputs" />');
        this.#container.append(inputsContainer);

        // Create all inputs
        for (const input of hw) {
            await this.#createInput(parser, inputsContainer, input);
        }
    }

    /**
     * Crate one input from a HW definition
     */
    async #createInput(parser, inputsContainer, inputDefinition) {
        const model = inputDefinition.data.model;

        let visualElement = null;
        let inputElement = null;

        switch (model.type) {
            case "AdafruitSwitch":
                inputsContainer.append(
                    // Switch element
                    inputElement = $('<div id="' + this.#options.domNamespace + '-switch-gp' + model.port + '" />')
                    .addClass(this.#options.domNamespace + '-switch')
                    // .data('port', model.port)
                    .append(
                        // Visual switch parts (LEDs)
                        visualElement = $('<div />')
                        .addClass(this.#options.domNamespace + '-switch-visual'),

                        // Overlay for hover effects and click handlers
                        $('<div />')
                        .addClass(this.#options.domNamespace + '-switch-overlay')
                        .on('mousedown touchstart', async function(e) {
                            e.currentTarget.parentNode.dataset.pushed = true;
                        })
                        .on('mouseup mouseout mouseleave touchend', async function(e) {
                            e.currentTarget.parentNode.dataset.pushed = false;
                        })
                    )
                );
                break;

            // default:
            //     throw new Error("Input type unknown: " + model.type);
        }

        // LEDs (can be added to any type, theoretically)
        if (inputDefinition.data.pixels) {
            const pixels = inputDefinition.data.pixels
            for (const pixel of pixels) {
                visualElement.append(
                    $('<div id="' + this.#options.domNamespace + '-led-' + pixel + '"/>')
                    .addClass(this.#options.domNamespace + "-led")
                )
            }
        }

        // Parser frontend
        await this.#initParserFrontend(parser, model, inputElement);
    }

    /**
     * Adds the parser frontend
     */
    async #initParserFrontend(parser, model, inputElement) {
        if (!inputElement) return;
        
        // Parser UI
        const input = await parser.input(model.port);
        if (!input) return;

        const actions = await input.actions();
        const actionsHold = await input.actions(true);
        
        inputElement.append(
            $('<div class="pyswitch-parser-frontend"  />').append(
                actions.map((item) =>
                    $('<span class="button actions" data-toggle="tooltip" title="Action on normal press" />')
                    .text(item.name)
                ),
                actionsHold.map((item) =>
                    $('<span class="button actions-hold" data-toggle="tooltip" title="Action on long press" />')
                    .text(item.name)
                )
            )
        )
    }
}