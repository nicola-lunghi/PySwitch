/**
 * Implements the PySwitch frontend (switches, LEDs etc.)
 */
class PySwitchFrontend {
    
    #controller = null;
    #options = null;
    #container = null;
    #elementsToHide = [];    // Elements to be removed on reset

    parserFrontend = null;

    /**
     * {
     *      domNamespace,
     *      globalContainer:   Container for additional inputs (see Device.isAdditionalInput())
     * }
     */
    constructor(controller, container, options) {
        this.#controller = controller;
        this.#container = container;
        this.#options = options;    
    }

    /**
     * Remove all controls and the display (to signal that a new UI is coming up)
     */
    reset() {
        for (const item of this.#elementsToHide) {
            item.hide();
        }
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
        this.#elementsToHide = [];
        this.#options.globalContainer.empty();
        
        this.#container.append(
            $('<img id="' + this.#options.domNamespace + '-background" />')
        );

        // Create parser frontend
        this.parserFrontend = new ParserFrontend(this.#controller, parser);

        // Add switches and LEDs etc.
        await this.#initInputs(parser);

        let canvasElement = null;
        this.#container.append(
            canvasElement = $('<canvas id="' + this.#options.domNamespace + '-display" />')
        );
        this.#elementsToHide.push(canvasElement);
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
        for (const inputDefinition of hw) {
            await this.#createInput(parser, inputsContainer, inputDefinition)            
        }

        // Init all frontend inputs
        await this.parserFrontend.init();
    }

    /**
     * Crate one input from a HW definition
     */
    async #createInput(parser, inputsContainer, inputDefinition) {
        const model = inputDefinition.data.model;
        const device = await parser.device();

        let visualElement = null;
        let inputElement = null;

        const container = device.isAdditionalInput(model) ? this.#options.globalContainer : inputsContainer;
        
        switch (model.type) {
            case "AdafruitSwitch":
                container.append(
                    // Switch element
                    inputElement = $('<div id="' + this.#options.domNamespace + '-switch-gp' + model.port + '" />')
                    .addClass(this.#options.domNamespace + '-switch')
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

            case "AdafruitPotentiometer":
                container.append(
                    // Continuous input element
                    inputElement = $('<div id="' + this.#options.domNamespace + '-potentiometer-gp' + model.port + '" />')
                    .addClass(this.#options.domNamespace + '-potentiometer')
                    .append(
                        visualElement = $('<input type="range" min="0" max="65535" />')
                        .addClass(this.#options.domNamespace + '-potentiometer-visual')
                    )
                );
                break;

            case "AdafruitEncoder":
                container.append(
                    // Rotary encoder element
                    inputElement = $('<div id="' + this.#options.domNamespace + '-encoder-gp' + model.port + '" />')
                    .addClass(this.#options.domNamespace + '-encoder')
                    .append(
                        visualElement = $('<input type="range" min="0" max="65535" />')
                        .addClass(this.#options.domNamespace + '-encoder-visual')
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

        if (visualElement) {
            this.#elementsToHide.push(visualElement);
        }

        // Parser frontend
        await this.parserFrontend.addInput(inputDefinition, inputElement);
    }
}