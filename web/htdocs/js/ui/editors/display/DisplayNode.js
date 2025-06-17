/**
 * Node handler, representing a display label
 */
class DisplayNode {

    id = null;         // Unique ID string

    node = null;       // Raw data node
    parent = null;     // Parent DisplayNode handler

    preview = null;    // Preview handler for the node
    type = null;       // DisplayNodeType handler (implementing all type specific stuff)
    
    editor = null;     // DisplayEditor base instance
    usages = [];

    constructor(editor, node, parentNodeHandler = null) {
        this.editor = editor;
        this.node = node;
        this.parent = parentNodeHandler;

        this.type = DisplayNodeType.getInstance(this);
        this.editor.references.set(node, this);

        this.id = Tools.uuid();
    }

    async destroy() {
        if (this.preview) {
            await this.preview.destroy();
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
        await this.type.setup();
        
        this.preview = new DisplayNodePreview(this);
        await this.preview.setup();

        this.usages = await this.#determineUsages();

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
     * Returns all usages in inputs.py, if assigned
     */
    async #determineUsages() {
        if (!this.node.assign) return [];
        return this.editor.getConfig().parser.checks.getDisplayUsages(this.node.assign, true);
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

        const children = this.getChildren();
        for(const child of children) {
            child.update();
        }
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
     * Returns the last child or null
     */
    firstChild() {
        const raw = this.getChildrenRaw();
        if (!raw) return null;
        return this.editor.references.get(raw[0]);
    }

    /**
     * Returns the last child or null
     */
    lastChild() {
        const raw = this.getChildrenRaw();
        if (!raw) return null;
        return this.editor.references.get(raw[raw.length-1]);
    }

    /**
     * Gets all siblings of the node (incl. the node itself)
     */
    getSiblings() {
        if (!this.parent) return [this];
        
        return this.parent.getChildren();
    }

    /**
     * Returns a flat list of node handlers contained (incl. this node).
     * options: {
     *     editable: true      Only collect editable nodes
     * }
     */
    flatten(options = {}) {
        function crawl(node) {
            let ret = [];

            if (options.editable) {
                if (node.type.editable()) {
                    ret.push(node);
                }
            } else {
                ret.push(node);
            }

            const children = node.getChildren();
            for(const child of children) {
                ret = ret.concat(crawl(child));
            }

            return ret;
        }

        return crawl(this);
    }

    /**
     * Searches for a node with the passed ID. Returns null if not found.
     */
    searchById(id) {
        if (this.id == id) return this;

        const children = this.getChildren();
        for(const child of children) {
            const ret = child.searchById(id);
            if (ret) return ret;
        }
        return null;
    }

    /**
     * Executes the callback for this node and all of its children (deep)
     */
    async each(callback) {
        await callback(this);        

        const children = this.getChildren();
        for(const child of children) {
            await child.each(callback);
        }
    }

    /**
     * Returns the model dimensions.
     */
    getModelBounds() {
        const boundsNode = this.type.getBoundsNode();
        if (!boundsNode) {
            throw new Error("No bounds parameter found for node");
        }
        
        function getDim(name) {
            const bnode = Tools.getArgument(boundsNode, name);
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
        // Set dimensions on model
        const boundsNode = this.type.getBoundsNode();
        if (!boundsNode) throw new Error("No bounds parameter found for node");
        
        function setDim(name, value) {
            const bnode = Tools.getArgument(boundsNode, name);
            if (!bnode) throw new Error("Dimension " + name + " not found");
            
            bnode.value = "" + Math.round(value);
        }

        setDim('x', bounds.x);
        setDim('y', bounds.y);
        setDim('w', (bounds.width >= 1) ? bounds.width : 1);
        setDim('h', (bounds.height >= 1) ? bounds.height : 1);

        if (this.preview) this.preview.update();
        this.editor.parameters.update();
    }

    /**
     * Select this node (not recursive)
     */
    async select() {
        await this.editor.select(this);
    }

    /**
     * Lets the node appear selected (UI only)
     */
    setSelected(selected) {
        if (!this.preview) return;
        this.preview.setSelected(selected);
    }

    /**
     * Clear the selection (recursive, internal use)
     */
    deselectAll() {
        this.setSelected(false);

        const children = this.getChildren();
        for(const child of children) {
            child.deselectAll();
        }
    }

    /**
     * Is this node selected?
     */
    selected() {
        return this.editor.selected == this;
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
        
        this.#updatePeers(siblings.value);
    }

    /**
     * Moves the label one step down among its siblings
     */
    moveDown() {
        if (!this.parent) return;

        const siblings = Tools.getArgument(this.parent.node, "children")

        const childIndex = this.getChildIndex();

        if (childIndex == 0) return;

        // Swap siblings
        siblings.value[childIndex] = siblings.value[childIndex - 1];
        siblings.value[childIndex - 1] = this.node;

        this.#updatePeers(siblings.value);        
    }

    /**
     * Moves the label one step up among its siblings
     */
    moveUp() {
        if (!this.parent) return;

        const siblings = Tools.getArgument(this.parent.node, "children")

        const childIndex = this.getChildIndex();

        if (childIndex >= siblings.value.length - 1) return;

        // Swap siblings
        siblings.value[childIndex] = siblings.value[childIndex + 1];
        siblings.value[childIndex + 1] = this.node;

        this.#updatePeers(siblings.value);  
    }

    /**
     * Adds a child from the given raw data node
     */
    addChild(node) {
        const handler = new DisplayNode(
            this.editor,
            node,
            this
        )

        const children = Tools.getArgument(this.node, "children");
        children.value.push(node);

        return handler;
    }

    /**
     * Remove node
     */
    remove() {
        if (!this.parent) return;

        this.parent.removeChild(this);
    }

    /**
     * Removes a child handler if found
     */
    removeChild(child) {
        if (child.isReferenced()) {
            throw new Error('Please remove all usages of ' + child.type.getName() + ' from inputs.py first');
        }

        const children = Tools.getArgument(this.node, "children")
        children.value = children.value.filter((node) => (node != child.node));
    }

    /**
     * Update the passed nodes and the parameter panel from the data model.
     */
    #updatePeers(nodesToUpdate = null) {
        for (const node of nodesToUpdate || []) {
            const handler = this.editor.references.get(node);
            if (!handler) throw new Error('Node not found in refs')

            handler.update();
        }

        this.editor.parameters.update();
    }

    /**
     * Checks if the label is used in inputs.py
     */
    isReferenced() {
        return this.usages.length > 0;
    }

    ////////////////////////////////////////////////////////////////////////////

    /**
     * Gets a list of all messages for this node.
     */
    getMessages() {
        return [].concat(
            this.#checkAssignmentExists(),
            this.#checkAssignmentReferenced()
        );
    }

    getMessagesDeep() {
        let ret = this.getMessages();

        const children = this.getChildren();
        for(const child of children) {
            ret = ret.concat(child.getMessages());
        }

        return ret;
    }

    /**
     * Checks if the assignment already exists
     */
    #checkAssignmentExists() {
        const ret = [];

        if (this.node.assign == "Splashes") {
            ret.push({
                type: 'E',
                message: 'Splashes is not an allowed display element name.',
                input: "assign"
            });
        }

        const that = this;
        this.editor.root
            .flatten()
            .forEach((node) => {
                if (node == that) return;
                if (!that.node.assign) return;

                if (node.node.assign == that.node.assign) {
                    ret.push({
                        type: 'E',
                        message: "Assignment " + that.node.assign + " already exists.",
                        input: "assign"
                    });
                }
            });
        
        return ret;
    }

    /**
     * Checks if the assignment is referenced
     */
    #checkAssignmentReferenced() {
        const ret = [];

        for(const usage of this.usages) {
            ret.push({
                type: 'I',
                message: 'Used in ' + usage.input.assignment.displayName,
                input: 'assign'
            })
        }

        return ret;
    }

    //////////////////////////////////////////////////////////////////////////////////////

    /**
     * Returns an arguments value
     */
    getParameter(name, defaultValue = null) {
        const valueNode = Tools.getArgument(this.node, name);

        if (!valueNode) return defaultValue;
        return valueNode.value;
    }

    /**
     * Sets a parameter on the data model
     */
    setParameter(name, value, defaultValue = null) {
        if (value == defaultValue) {
            // Remove parameter
            this.node.arguments = this.node.arguments.filter((entry) => (entry.name != name));

        } else {
            // Set/add parameter
            let valueNode2 = Tools.getArgument(this.node, name);
            if (!valueNode2) {
                this.node.arguments.push(valueNode2 = {
                    name: name
                })
            }
            valueNode2.value = value;
        }

        this.update();
    }

    /////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Set a new node type (overrides name and arguments)
     */
    async setType(type, client) {
        if (this.node.name == type) return;

        this.node.name = type;
        this.node.client = client;

        const boundsNode = this.type.getBoundsNode();
        if (!boundsNode) throw new Error("No bounds parameter found for node");

        // Get new args. For this we use a dummy type handler
        this.node.arguments = DisplayNodeType.getInstance(this).getDefaultArguments().concat({
            name: "bounds",
            value: boundsNode
        });
        console.log(this.node.arguments)

        // Now there are all params, we can initialize the final type handler
        this.type = DisplayNodeType.getInstance(this);
        await this.type.setup();

        // Update preview
        await this.preview.destroy();
        await this.preview.setup();
        await this.preview.init();

        this.preview.update();
    }
}