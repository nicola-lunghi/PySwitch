/**
 * Implements the PySwitch frontend (switches, LEDs etc.)
 */
class PySwitchFrontend {
    
    #controller = null;
    #options = null;
    #container = null;
    parserFrontend = null;
    #elementsToHide = [];    // Elements to be removed on reset

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
        
        this.#container.append(
            $('<img id="' + this.#options.domNamespace + '-background" />')
        );

        // Create parser frontend
        this.parserFrontend = new ParserFrontend(this.#controller, parser);

        // Add switches and LEDs
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
            await this.#createInput(inputsContainer, inputDefinition)            
        }

        // Init all frontend inputs
        await this.parserFrontend.init();
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

        if (visualElement) {
            this.#elementsToHide.push(visualElement);
        }

        // Parser frontend
        await this.parserFrontend.addInput(model.port, inputElement);
    }
}