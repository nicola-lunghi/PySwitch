/**
 * Enable/kill drag functionality for a node handler
 */
class DisplayNodeDrag {

    #nodeHandler = null;
    #preview = null;

    constructor(preview, nodeHandler) {
        this.#preview = preview;
        this.#nodeHandler = nodeHandler;
    }

    /**
     * Stop interact.js
     */
    kill() {
        interact(this.#nodeHandler.preview.element[0]).unset();
    }

    /**
     * Make the passed element draggable
     */
    init() {
        const that = this;
        const element = this.#nodeHandler.preview.element;

        interact(element[0])
            .draggable({
                listeners: {
                    start (event) {
                        try {
                            that.#nodeHandler.select();
                            that.#nodeHandler.toFront();

                        } catch (e) {
                            that.#preview.controller.handle(e);
                        }
                    },
                    move (event) {
                        const bounds = that.#nodeHandler.getModelBounds();

                        bounds.x += event.dx / that.#preview.scaleFactor;
                        bounds.y += event.dy / that.#preview.scaleFactor;

                        that.#nodeHandler.setModelBounds(bounds);
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
            })
            .resizable({
                // Resize from all edges and corners
                edges: { right: true, bottom: true },

                listeners: {
                    start (event) {
                        try {
                            that.#nodeHandler.select();
                            that.#nodeHandler.toFront();

                        } catch (e) {
                            that.#preview.controller.handle(e);
                        }
                    },
                    move (event) {
                        const bounds = that.#nodeHandler.getModelBounds();

                        bounds.width = event.rect.width / that.#preview.scaleFactor;
                        bounds.height = event.rect.height / that.#preview.scaleFactor;

                        that.#nodeHandler.setModelBounds(bounds);

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