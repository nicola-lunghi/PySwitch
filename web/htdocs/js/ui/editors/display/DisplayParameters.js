/**
 * Parameters for display editor
 */
class DisplayParameters {
    
    #editor = null;
    container = null;

    #selector = null;
    #parametersElement = null;
    #parametersList = null;

    constructor(editor) {
        this.#editor = editor;
    }

    async destroy() {        
    }

    /**
     * Creates the DOM
     */
    async get() {
        return this.container = $('<div class="display-parameters-container" />')
    }

    /**
     * Re-build according to the data model
     */
    async reset() {
        const that = this;

        // Clear
        this.container
            .empty()
            .append(
                $('<span class="display-parameters-header" />"').append(
                    // Selector
                    this.#selector = $('<select class="display-selector" data-toggle="tooltip" title="Select an element to edit its parameters" />')
                    .prop('name', 'select-display')
                    .on('change', async function() {
                        try {
                            const id = $(this).val();
                            if (!id) {
                                $(this).val(that.#editor.selected.id);
                                return;
                            }
                            
                            const node = that.#editor.root.searchById(id);

                            await node.select();

                        } catch (e) {
                            that.#editor.controller.handle(e);
                        }
                    }),

                    // Add button
                    $('<span class="button fas fa-plus" data-toggle="tooltip" title="Add a new element" />')
                    .on('click', async function() {
                        try {
                            await that.#editor.createElement();                            

                        } catch (e) {
                            that.#editor.controller.handle(e);
                        }
                    }),

                    // Remove button
                    $('<span class="button fas fa-trash" data-toggle="tooltip" title="Remove the selected element..." />')
                    .on('click', async function() {
                        try {
                            const selected = that.#editor.selected;
                            if (!selected) return;
                            if (selected.isReferenced()) {
                                alert('Please remove all usages of ' + selected.type.getName() + ' from inputs.py first');
                                return;
                            }

                            if (!confirm('Do you really want to delete the selected element?')) return;
                            
                            selected.remove();
                            
                            await that.#editor.reset();

                        } catch (e) {
                            that.#editor.controller.handle(e);
                        }
                    })
                ),

                // Parameters
                this.#parametersElement = $('<div class="display-parameters" />')
            );

        this.#updateSelector();
    }

    /**
     * Selects the passed node (UI only, internal)
     */
    async select(node) {
        if (!node) {
            this.#selector.val("");
            return;
        }

        if (!(node instanceof DisplayNode)) throw new Error('Invalid node');
        this.#selector.val(node.id);

        await this.#showNode(node);
    }

    /**
     * Updates the selected parameters from the data model
     */
    update() {
        // Parameters of selected node
        if (this.#parametersList) {
            this.#parametersList.update()
        }

        // Selector
        this.#updateSelector();
    }

    /**
     * Shows parameters for the node
     */
    async #showNode(node) {
        this.#parametersElement
            .empty()
            .append(
                await (this.#parametersList = new DisplayParameterList(node)).get()
            );
    }

    /**
     * Set up the displays selector
     */
    #updateSelector() {
        if (!this.#selector) return;
        
        const that = this;
        this.#selector
            .empty()
            .append(
                $('<option />')
                .prop('value', '')
                .text('Select a label...'),

                this.#editor.root.flatten({
                    editable: true
                })
                .map(function(node) {
                    const ret = $('<option />')
                        .prop('value', node.id)
                        .text(node.type.getName());

                    if (that.#editor.selected == node) {
                        ret.prop('selected', true)
                    }

                    return ret;
                })
            );
    }
}