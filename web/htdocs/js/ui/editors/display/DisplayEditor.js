/**
 * Implements the display editor
 */
class DisplayEditor {
    
    controller = null;
    #container = null;   // Container element

    preview = null;      // Preview area handler
    parameters = null;   // Parameters area handler

    splashes = null;     // Splashes data node
    #rootNode = null;    // Editor container data node

    root = null;         // Root node handler
    references = null;   // Memory for node references (node -> handler)
    
    selected = null;     // Selected node handler, if any

    availableCallbacks = null;   // Buffer

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
        // Available callbacks
        this.availableCallbacks = (await this.getConfig().parser.getAvailableCallbacks());

        // Get raw splashes tree (deep copy, because we do not want to alter the parser data yet)
        this.splashes = JSON.parse(JSON.stringify(this.getConfig().parser.splashes()));

        // Get the editing root node
        this.#rootNode = this.#getSplashesRootElement(this.splashes);

        await this.reset();

        await this.preview.init();
    }

    /**
     * Returns the root node for the editor
     */
    #getPersistentRootNode() {
        const splashes = this.getConfig().parser.splashes();
        return this.#getSplashesRootElement(splashes);
    }

    /**
     * Buffered
     */
    getCallbackDefinition(name, clientId = null, target = null) {
        for (const cl of this.availableCallbacks) {
            if (clientId && cl.client != clientId) continue;

            for (const cb of cl.callbacks) {
                if (target && cb.target != target) continue;
                if (cb.name != name) continue;

                return cb;
            }
        }
    }

    /**
     * Sets a new splashes callback
     */
    async setSplashesCallback(name) {
        if (this.splashes.name == name) return;

        const definition = this.getCallbackDefinition(name);
        if (!definition) {
            throw new Error("Unknown Callbacks cannot be changed.");
        }

        if (!definition.meta.data.splashRootParameter) {
            throw new Error('No splashRootParameter defined for ' + name);
        }

        this.splashes = {
            name: name,
            client: definition.meta.client.id,
            arguments: definition.parameters          // Only add params without defaults
                .filter((param) => !param.default)
                .map((param) => {
                    if (param.name == definition.meta.data.splashRootParameter) {
                        return {
                            name: definition.meta.data.splashRootParameter,
                            value: this.#rootNode
                        }
                    } else {
                        return {
                            name: param.name,
                            value: param.meta.getDefaultValue()
                        }
                    }
                })
        }

        await this.reset()
    }

    /**
     * Returns the Display Element which is the parent for all labels (root element).
     */
    #getSplashesRootElement(splashes) {
        const that = this;

        const definition = this.getCallbackDefinition(splashes.name, splashes.client, "Splashes");

        if (!definition) {
            throw new Error('No definition found for ' + splashes.name);
        }
        if (!definition.meta.data.splashRootParameter) {
            throw new Error('No splashRootParameter defined for ' + splashes.name);
        }

        const splash = Tools.getArgument(splashes, definition.meta.data.splashRootParameter);
        if (!splash) throw new Error("No " + definition.meta.data.splashRootParameter + " parameter found for " + splashes.name);

        return splash.value;
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
        const newSplashes = this.splashes; //this.#createSplashes();
        const parser = this.getConfig().parser;

        await this.controller.restart({
            message: "none",
            changeCallback: async function() {
                await parser.setSplashes(newSplashes);
            }
        });
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