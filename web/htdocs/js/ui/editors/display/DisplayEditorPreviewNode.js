/**
 * Implements the display editor
 */
class DisplayEditorPreviewNode {

    node = null;
    element = null;
    parent = null;

    #preview = null;

    constructor(preview, node, parentNodeHandler = null) {
        this.#preview = preview;
        this.node = node;
        this.parent = parentNodeHandler;

        this.#preview.references.set(node, this);
    }

    /**
     * Sets up the element and returns it (recursive)
     */
    initElement() {
        this.element = $('<span class="display-element" />');
        
        switch(this.node.name) {
            case "DisplayLabel":
                this.#renderDisplayLabel();
                break;
        }

        // Label text
        const text = this.#getDisplayElementText();
        this.element
            .text(text)
            .attr('data-toggle', 'tooltip')
            .attr('title', text);

        // Recurse to children, if any. Fist let the client determine which children to show.
        const children = this.getChildrenRaw();
        
        // We have children: Recurse and append them
        for (const child of children) {
            const childHandler = new DisplayEditorPreviewNode(
                this.#preview,
                child, 
                this
            )

            this.element.append(
                childHandler.initElement()
            );
        }

        // Set properties
        this.#update();

        return this.element;
    }

    /**
     * Initialize after the hierarchy has been set up
     */
    init() {
        if (this.editable()) {
            // Make editable
            (new DisplayEditorPreviewNodeDrag(this.#preview, this)).init();
        }

        const children = this.getChildren();
        for(const child of children) {
            child.init();
        }
    }

    /**
     * Renders a DisplayLabel node. Returns DOM.
     */
    #renderDisplayLabel() {
        const that = this;
        this.element
            .addClass('display-label')
            .addClass('editable')
            .on('click', async function() {
                try {
                    that.select();
                    
                } catch (e) {
                    that.#preview.controller.handle(e);
                }
            })
    }

    /**
     * Generates the label text
     */
    #getDisplayElementText() {
        if (this.node.hasOwnProperty("assign")) return this.node.assign;
        
        const callback = Tools.getArgument(this.node, "callback");
        if (callback) return callback.value.name;
        
        return "";
    }

    /**
     * Sets the properties of the element from the model
     */
    #update() {
        // Bounds
        try {
            const bounds = this.getModelBounds();
            this.#setDisplayElementBounds({
                x: bounds.x * this.#preview.scaleFactor,
                y: bounds.y * this.#preview.scaleFactor,
                width: bounds.width * this.#preview.scaleFactor,
                height: bounds.height * this.#preview.scaleFactor,
            })

        } catch(e) {
            // console.warn(e);
            this.#setDisplayElementBounds({
                x: 0,
                y: 0,
                width: 0,
                height: 0
            });
        }

        // Order
        this.element.css('z-index', this.getChildIndex());
    }

    /**
     * Returns if the node can be edited
     */
    editable() {
        return this.element.hasClass('editable');
    }

    /**
     * Returns the index of this node among its siblings
     */
    getChildIndex() {
        if (!this.parent) return 0;
        
        const pChildren = this.parent.getChildrenRaw();
        if (!pChildren) return 0;

        for (let i = 0; i<pChildren.length; ++i) {
            if (pChildren[i] == this.node) return i;
        }

        throw new Error("INTERNAL ERROR: Could not find child among its siblings");
    }

    /**
     * Returns the children of the node (as raw data models)
     */
    getChildrenRaw() {
        const children = Tools.getArgument(this.node, "children")
        if (children) {
            return children.value;
        }

        return [];
    }

    /**
     * Array of child node handlers
     */
    getChildren() {
        const raw = this.getChildrenRaw();

        return raw.map((el) => this.#preview.references.get(el));
    }

    /**
     * Puts the element to front inside its parent
     */
    toFront() {
        if (!this.parent) return;

        const siblings = Tools.getArgument(this.parent.node, "children")

        const that = this;
        siblings.value.sort((a, b) => {
            if (a == that.node) return 1;
            if (b == that.node) return -1;
            return 0;
        })
        
        for (const siblingNode of siblings.value) {
            const handler = this.#preview.references.get(siblingNode);
            handler.#update();
        }
    }

    /**
     * Returns the model dimensions.
     */
    getModelBounds() {
        const boundsNode = Tools.getArgument(this.node, "bounds");
        if (!boundsNode) throw new Error("No bounds parameter found for node");
        
        function getDim(name) {
            const bnode = Tools.getArgument(boundsNode.value, name);
            if (!bnode) return 0;
            return parseInt((new Resolver()).resolve(bnode.value));
        }
        
        return {
            x: getDim('x'),
            y: getDim('y'),
            width: getDim('w'),
            height: getDim('h')
        };
    }

    /**
     * Sets model dimensions
     */
    setModelBounds(bounds) {
        const that = this;

        // Set dimensions on model
        const boundsNode = Tools.getArgument(this.node, "bounds");
        if (!boundsNode) throw new Error("No bounds parameter found for node");
        
        function setDim(name, value) {
            const bnode = Tools.getArgument(boundsNode.value, name);
            if (!bnode) throw new Error("Dimension " + name + " not found");
            
            bnode.value = "" + Math.round(value);
        }

        setDim('x', bounds.x);
        setDim('y', bounds.y);
        setDim('w', bounds.width);
        setDim('h', bounds.height);

        // Set dimensions on DOM element
        function scaleDim(v) {
            return v * that.#preview.scaleFactor;
        }

        this.#setDisplayElementBounds({
            x: scaleDim(bounds.x),
            y: scaleDim(bounds.y),
            width: scaleDim(bounds.width),
            height: scaleDim(bounds.height),
        });
    }

    /**
     * Retunrs the bounds of a display element
     *
    #getDisplayElementBounds() {
        return {
            x: parseFloat(this.element.css('left')),
            y: parseFloat(this.element.css('top')),
            width: parseFloat(this.element.css('width')),
            height: parseFloat(this.element.css('height'))
        }
    }

    /**
     * Sets the bounds of a display element (model coords)
     */
    #setDisplayElementBounds(bounds) {
        this.element
            .css('left', bounds.x + "px")
            .css('top', bounds.y + "px")
            .css('width', bounds.width + "px")
            .css('height', bounds.height + "px")
    }

    /**
     * Select this node (not recursive)
     */
    select() {
        if (this.#preview.selected == this) return;

        this.#preview.root.deselectAll();

        this.element.addClass('selected');

        this.#preview.selected = this;
    }

    /**
     * Clear the selection (recursive)
     */
    deselectAll() {
        this.element.removeClass('selected');

        const children = this.getChildren();
        for(const child of children) {
            child.deselectAll();
        }
    }
}