/**
 * Implements the display editor
 */
class DisplayEditor {
    
    controller = null;
    #container = null;   // Container element

    preview = null;      // Preview area handler
    parameters = null;   // Parameters area handler

    #rootNode = null;    // Raw data tree root
    root = null;         // Root node handler
    references = null;   // Memory for node references (node -> handler)
    
    selected = null;     // Selected node handler, if any

    constructor(controller) {
        this.controller = controller;        
    }
    
    /**
     * Destroy the editor
     */
    async destroy() {
        if (this.preview) {
            await this.preview.destroy();
        }
        if (this.parameters) {
            await this.parameters.destroy();
        }
        if (this.root) {
            await this.root.destroy();
        }
    }

    /**
     * Generate the DOM for the properties panel, or null if no options are present.
     */
    async get() {
        this.#container = $('<div class="display-editor" />')

        let previewContainer = null;
        this.#container.append(
            // Preview
            previewContainer = $('<div class="display-preview-container" />'),

            // Parameters
            await (this.parameters = new DisplayParameters(this)).get()
        );

        previewContainer.append(
            await (this.preview = new DisplayPreview(this, previewContainer)).get()
        );

        return this.#container;
    }

    /**
     * Called after get()
     */
    async init() {
        // Get raw splashes tree (deep copy, because we do not want to alter the parser data yet)
        this.#rootNode = JSON.parse(JSON.stringify(this.#getPersistentRootNode()));

        await this.reset();

        await this.preview.init();
    }

    /**
     * Returns the root node for the editor
     */
    #getPersistentRootNode() {
        const splashes = this.getConfig().parser.splashes();

        // The root element may be client dependent
        const client = this.getClient(); //ClientFactory.getInstance(splashes.client ? splashes.client : "local");

        // Get raw splashes tree (deep copy, because we do not want to alter the parser data yet)
        return client.getSplashesRootElement(splashes);
    }

    /**
     * Resets the app to the current data model, refreshing the display
     */
    async reset() {
        // Clear old handlers etc.
        this.selected = null;
        if (this.root) await this.root.destroy();

        this.references = new Map();
        
        // Create new root from the existing data model
        this.root = new DisplayNode(
            this,
            this.#rootNode
        );

        // Create element hierarchy
        await this.root.setup();

        // Attach to DOM
        await this.preview.reset();
        await this.parameters.reset();

        // Update view
        this.root.update();

        // Init interact.js etc. after the hierarchy is set up and attached
        await this.root.init();
    }

    /**
     * Update everything to the data model.
     */
    update() {
        this.root.update();
        this.parameters.update();
    }

    /**
     * Create a new element on top
     */
    async createElement() {
        let assign = "DISPLAY_LABEL_1";
        let cnt = 2;
        while (this.root.flatten().filter((node) => node.node.assign == assign).length > 0) {
            assign = "DISPLAY_LABEL_" + cnt++;
        }

        this.root.addChild({
            name: "DisplayLabel",
            assign: assign,
            arguments: [
                {
                    name: "bounds",
                    value: {
                        name: "DisplayBounds",
                        arguments: [
                            {
                                name: 'x',
                                value: '0'
                            },
                            {
                                name: 'y',
                                value: '0'
                            },
                            {
                                name: 'w',
                                value: '100'
                            },
                            {
                                name: 'h',
                                value: '30'
                            }
                        ]
                    }
                },
                {
                    name: "layout",
                    value: {
                        arguments: [
                            {
                                name: "font",
                                value: '"/fonts/H20.pcf"'
                            },
                            {
                                name: "backColor",
                                value: 'DEFAULT_LABEL_COLOR'
                            },
                            {
                                name: "stroke",
                                value: '1'
                            }
                        ]
                    }
                }
            ]
        });

        await this.reset();

        // The new label is always on top, so we can just select the top element
        this.root.lastChild().select();
    }

    /**
     * Apply the changes to the current config
     */
    async apply() {
        const newSplashes = this.#createSplashes();
        const parser = this.getConfig().parser;

        await this.controller.restart({
            message: "none",
            changeCallback: async function() {
                await parser.setSplashes(newSplashes);
            }
        });
    }

    /**
     * Returns a new splashes object to be set on the configuration
     */
    #createSplashes() {
        // Get raw splashes tree (deep copy, because we do not want to alter the parser data yet)
        const splashes = JSON.parse(JSON.stringify(this.getConfig().parser.splashes()));

        // The root element may be client dependent
        const client = this.getClient(); //ClientFactory.getInstance(splashes.client ? splashes.client : "local");

        // Set the new root node in the splashes
        if (client.setSplashesRootElement(splashes, this.#rootNode)) {
            return splashes;
        }

        this.#rootNode.assign = "Splashes";

        return this.#rootNode;
    }

    /**
     * Determine the client for the configuration
     */
    getClient() {
        const splashes = this.getConfig().parser.splashes();
        return ClientFactory.getInstance(splashes.client ? splashes.client : "local");
    }

    /**
     * Returns the configuration to use
     */
    getConfig() {
        return this.controller.currentConfig;
    }

    /**
     * Returns all messages
     */
    getMessages() {
        return this.root.getMessagesDeep();
    }

    /**
     * True if the user did changes.
     */
    isDirty() {
        return JSON.stringify(this.#getPersistentRootNode()) != JSON.stringify(this.root.node);
    }

    /**
     * Selects a node handler
     */
    async select(node) {
        // if (!(node instanceof DisplayNode)) throw new Error('Invalid node');
        if (this.selected == node) return;

        this.deselect();
        this.selected = node;

        if (node) {
            node.setSelected(true);
        }
        await this.parameters.select(node);
    }

    /**
     * Clear the selection
     */
    deselect() {
        this.root.deselectAll();

        this.selected = null;
    }
}