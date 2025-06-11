/**
 * Enable/kill drag functionality for a node handler
 */
class DisplayNodePreviewDrag {

    #handler = null;
    #preview = null;

    constructor(preview, nodeHandler) {
        this.#preview = preview;
        this.#handler = nodeHandler;
    }

    /**
     * Stop interact.js
     */
    kill() {
        interact(this.#handler.preview.element[0]).unset();
    }

    /**
     * Make the passed element draggable
     */
    init() {
        const that = this;
        const element = this.#handler.preview.element;

        interact(element[0])
            .draggable({
                listeners: {
                    async start (event) {
                        try {
                            await that.#handler.select();
                            that.#handler.toFront();

                        } catch (e) {
                            that.#preview.controller.handle(e);
                        }
                    },
                    move (event) {
                        const bounds = that.#handler.getModelBounds();

                        bounds.x += event.dx / that.#preview.scaleFactor;
                        bounds.y += event.dy / that.#preview.scaleFactor;

                        that.#handler.setModelBounds(bounds);
                    }
                },

                modifiers: [
                    interact.modifiers.snap({
                        targets: [
                            interact.snappers.grid({ x: 10 * that.#preview.scaleFactor, y: 10 * that.#preview.scaleFactor })
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
            });

        if (!this.#handler.type.resizable()) return;

        interact(element[0])
            .resizable({
                // Resize from all edges and corners
                edges: { right: true, bottom: true },

                listeners: {
                    async start (event) {
                        try {
                            await that.#handler.select();
                            that.#handler.toFront();

                        } catch (e) {
                            that.#preview.controller.handle(e);
                        }
                    },
                    move (event) {
                        const bounds = that.#handler.getModelBounds();

                        bounds.width = event.rect.width / that.#preview.scaleFactor;
                        bounds.height = event.rect.height / that.#preview.scaleFactor;

                        that.#handler.setModelBounds(bounds);

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
                            interact.snappers.grid({ x: 10 * that.#preview.scaleFactor, y: 10 * that.#preview.scaleFactor })  // TODO not working for non-rect screens
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
                        min: { width: that.#preview.scaleFactor, height: that.#preview.scaleFactor }
                    })
                ],

                origin: 'parent'
            });
    }
}