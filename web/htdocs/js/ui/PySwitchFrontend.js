class PySwitchFrontend {
    
    #controller = null;
    #options = null;
    #container = null;
    parserFrontend = null;

    constructor(controller, container, options) {
        this.#controller = controller;
        this.#container = container;
        this.#options = options;    
        
        if (!this.#options.basePath) this.#options.basePath = ""
    }

    /**
     * Initialize to a given set of inputs and splashes
     */
    async apply(parser) {
        if (this.parserFrontend) {
            await this.parserFrontend.destroy();
            this.parserFrontend = null;
        }

        const device = await parser.device();
        this.#container[0].className = device.getDeviceClass();

        // Clear contents and create container
        this.#container.empty();
        
        this.#container.append(
            $('<img id="' + this.#options.domNamespace + '-background" />'),
            $('<canvas id="' + this.#options.domNamespace + '-display" />')
        );

        // Create parser frontend
        this.parserFrontend = new ParserFrontend(this.#controller, parser, this.#options.basePath);

        // Add switches and LEDs
        await this.#initInputs(parser);
    }

    /**
     * Creates DOM elements for all inputs and LEDs.
     */
    async #initInputs(parser) {
        const hw = await parser.getHardwareInfo();
        
        // Create container for all inputs
        const inputsContainer = $('<div id="' + this.#options.domNamespace + '-inputs" />');
        this.#container.append(inputsContainer);

        // Create all inputs
        for (const input of hw) {
            await this.#createInput(inputsContainer, input)            
        }
    }

    /**
     * Crate one input from a HW definition
     */
    async #createInput(inputsContainer, inputDefinition) {
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
        await this.parserFrontend.addInput(model, inputElement);
    }
}