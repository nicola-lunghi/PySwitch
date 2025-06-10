/**
 * Node handler, connection data model and UI
 */
class DisplayNode {

    node = null;
    parent = null;

    editor = null;

    editable = false;
    preview = null;
    parameters = null;
    
    constructor(editor, node, parentNodeHandler = null) {
        this.editor = editor;
        this.node = node;
        this.parent = parentNodeHandler;

        this.editor.references.set(node, this);
    }

    async destroy() {
        if (this.preview) {
            await this.preview.destroy();
        }  
        if (this.parameters) {
            await this.parameters.destroy();
        }        

        const children = this.getChildren();
        for (const child of children) {
            await child.destroy();
        }
    }

    /**
     * Sets up the element and returns it (recursive)
     */
    async setup() {
        switch(this.node.name) {
            case "DisplayLabel":
                this.editable = true;
                break;
        }
        
        this.preview = new DisplayNodePreview(this);
        await this.preview.setup();

        if (this.editable) {
            this.parameters = new DisplayNodeParameters(this);
            await this.parameters.setup();

            // Collect editable parameters
            this.editor.parameters.container.append(
                this.parameters.element
            )
        }

        // Recurse to children, if any. Fist let the client determine which children to show.
        const children = this.getChildrenRaw();
        
        // We have children: Recurse and append them
        for (const child of children) {
            const childHandler = new DisplayNode(
                this.editor,
                child, 
                this
            )

            await childHandler.setup();

            // Build preview hierarchy
            this.preview.element.append(
                childHandler.preview.element
            );
        }
    }

    /**
     * Initialize after the hierarchy has been set up
     */
    init() {
        this.preview.init();

        const children = this.getChildren();
        for(const child of children) {
            child.init();
        }
    }

    /**
     * Sets the properties of the element from the model
     */
    update() {
        this.preview.update();
        if (this.parameters) {
            this.parameters.update();
        }

        const children = this.getChildren();
        for(const child of children) {
            child.update();
        }
    }

    /**
     * Generates the label text
     */
    getText() {
        if (this.node.hasOwnProperty("assign")) return this.node.assign;
        
        const callback = Tools.getArgument(this.node, "callback");
        if (callback) return callback.value.name;
        
        return "";
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
     * Returns the children of the node (as raw data model nodes)
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
        const that = this;
        return raw.map((node) => {
            return that.editor.references.get(node);
        });
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
            const handler = this.editor.references.get(siblingNode);
            handler.update();
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

        this.preview.update();
        if (this.parameters) {
            this.parameters.update();
        }
    }

    /**
     * Select this node (not recursive)
     */
    select() {
        if (this.editor.selected == this) return;

        this.editor.root.deselectAll();

        this.preview.setSelected(true);
        if (this.parameters) {
            this.parameters.setSelected(true);
        }

        this.editor.selected = this;
    }

    /**
     * Clear the selection (recursive)
     */
    deselectAll() {
        this.preview.setSelected(false);
        if (this.parameters) {
            this.parameters.setSelected(false);
        }

        const children = this.getChildren();
        for(const child of children) {
            child.deselectAll();
        }
    }
}