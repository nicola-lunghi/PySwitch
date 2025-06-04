/**
 * Implements the display editor
 */
class DisplayEditor extends ParameterList {
    
    #preview = null;
    #container = null;

    #scaleFactor = 1;
    
    /**
     * Generate the DOM for the properties panel, or null if no options are present.
     */
    async get() {
        return this.#container = $('<div class="display-editor" />').append(
            this.#preview = $('<div class="display-preview" />')
        )
    }

    /**
     * Called after get()
     */
    async init() {
        await this.#update();
    }

    /**
     * Update the editor to the current state
     */
    async #update() {
        const config = this.controller.currentConfig;

        // Get raw splashes tree
        const splashes = config.parser.splashes();

        // Clear
        this.#preview.empty();

        // Get scale factor (determined by the device)
        const dim = await this.#determineScaleFactor(config);
        this.#preview
            .width(dim[0])
            .height(dim[1]);

        // Render elements
        this.#preview.append(
            await this.renderDisplayElement(splashes)
        );

        // Setup Interact.js after the DOM is ready
        this.#initDragging(this.#preview);
    }

    #initDragging(element) {
        if (element != this.#preview) {     // TODO exclude root element       
            this.#initInteract(element);
        }

        const that = this;
        element.children().each(function() {
            that.#initDragging($(this));
        });
    }

    #initInteract(element) {
        const that = this;

        interact(element[0])
            .draggable({
                listeners: {
                    /*start (event) {
                        console.log(event.type, event.target)
                    },*/
                    move (event) {
                        element.data("x", element.data("x") + event.dx);
                        element.data("y", element.data("y") + event.dy);

                        element.css("left", element.data("x") + "px");
                        element.css("top", element.data("y") + "px");
                    }
                },

                modifiers: [
                    interact.modifiers.snap({
                        targets: [
                            interact.snappers.grid({ x: 10 * that.#scaleFactor, y: 10 * that.#scaleFactor })  // TODO not working for non-rect screens
                        ],
                        range: Infinity,
                        relativePoints: [ { x: 0, y: 0 } ]
                    }),

                    interact.modifiers.restrict({
                        restriction: element[0].parentNode,
                        elementRect: { top: 0, left: 0, bottom: 1, right: 1 }                    
                    })                    
                ],

                inertia: true,
                origin: 'parent'
            })
            .resizable({
                // Resize from all edges and corners
                edges: { right: true, bottom: true },

                listeners: {
                    move (event) {
                        // Update the element's style
                        element.css("width", event.rect.width + 'px');
                        element.css("height", event.rect.height + 'px');

                        // // Translate when resizing from top or left edges
                        // x += event.deltaRect.left;
                        // y += event.deltaRect.top;

                        // element.data("x", element.data("x") + event.deltaRect.left);
                        // element.data("y", element.data("y") + event.deltaRect.top);
                        
                        // element.css("left", element.data("x") + "px");
                        // element.css("top", element.data("y") + "px");
                    }
                },

                modifiers: [
                    interact.modifiers.snap({
                        targets: [
                            interact.snappers.grid({ x: 10 * that.#scaleFactor, y: 10 * that.#scaleFactor })  // TODO not working for non-rect screens
                        ],
                        range: Infinity,
                        relativePoints: [ { x: 0, y: 0 } ]
                    }),

                    // Keep the edges inside the parent
                    interact.modifiers.restrictEdges({
                        outer: 'parent'
                    }),

                    // Minimum size
                    interact.modifiers.restrictSize({
                        min: { width: that.#scaleFactor, height: that.#scaleFactor }
                    })
                ],

                origin: 'parent'
            });
    }

    /**
     * Determines scale factor and sets it. Returns the display dimensions on screen.
     */
    async #determineScaleFactor(config) {
        const displayDimensions = (await Device.getInstance(config)).getDisplayDimensions();
        const displayWidth = displayDimensions[0];
        const displayHeight = displayDimensions[1];

        this.#scaleFactor = 2;

        return [displayWidth * 2, displayHeight * 2]
        // TODO
        

        // const availableWidth = this.#container.width()
        // const availableHeight = this.#container.height()

        // if (availableHeight < availableWidth) {
        //     this.#scaleFactor = availableHeight / displayHeight;
        //     return availableHeight - 2;
        // } else {
        //     this.#scaleFactor = availableWidth / displayWidth;
        //     return availableWidth - 2;
        // }
    }

    /**
     * Called by the client, this renders the editor for the given root DisplayElement node.
     * Returns DOM.
     */
    async renderDisplayElement(node) {
        // Let the client render the element
        const client = ClientFactory.getInstance(node.client ? node.client : "local");
        let ret = await client.renderDisplayElement(node, this);      

        if (!ret) {
            // Client did not render
            switch(node.name) {
                case "DisplayLabel":
                    ret = await this.#renderDisplayLabel(node);
                    break;

                default:
                    ret = $('<span />');
                    break;
            }
        }

        ret.addClass("display-element");

        // Position and Size, handles etc.
        this.#setupDisplayElement(node, ret);

        // Recurse to children, if any
        const children = Tools.getArgument(node, "children");
        if (!children) return ret;

        for (const child of children.value) {
            ret.append(
                await this.renderDisplayElement(child)
            );
        }

        return ret;
    }

    /**
     * Renders a DisplayLabel node. Returns DOM.
     */
    async #renderDisplayLabel(label) {
        return $('<span class="display-label" />');
    }

    /**
     * Sets the bounds of a DisplayElement node on the passed DOM element.
     */
    #setupDisplayElement(node, domElement) {
        const bounds = Tools.getArgument(node, "bounds");
        if (!bounds) return;

        const that = this;
        function getBoundsParam(name) {
            const node = Tools.getArgument(bounds.value, name);
            if (!node) return 0;
            return (new Resolver()).resolve(node.value) * that.#scaleFactor;
        }

        const x = getBoundsParam("x");
        const y = getBoundsParam("y");
        const w = getBoundsParam("w");
        const h = getBoundsParam("h");

        // console.log(x, y, w, h)

        function getText() {
            if (node.hasOwnProperty("assign")) return node.assign;
            
            const callback = Tools.getArgument(node, "callback");
            if (callback) return callback.value.name;
            
            return "";
        }

        domElement
            .css('left', x + "px")
            .css('top', y + "px")
            .css('width', w + "px")
            .css('height', h + "px")
            .data("x", x)
            .data("y", y)
            .text(getText())
    }
}