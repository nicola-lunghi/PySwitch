/**
 * Parameters for display editor
 */
class DisplayParameters {
    
    #editor = null;
    container = null;

    #selector = null;
    #parametersElement = null;
    #parameterLists = null;

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
                                await that.#editor.select();
                                return;
                            }
                            
                            const node = that.#editor.root.searchById(id);
                            await node.select();

                        } catch (e) {
                            that.#editor.controller.handle(e);
                        }
                    }),

                    // General settings button
                    $('<span class="button fas fa-wrench" data-toggle="tooltip" title="General settings" />')
                    .on('click', async function() {
                        try {
                            await that.#editor.select();

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
                            
                            if (!confirm('Do you really want to delete ' + selected.type.getName() + '?')) return;
                            
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

        await this.#showGeneralParams();
    }

    async rebuild() {
        await this.select(this.#editor.selected);
    }

    /**
     * Selects the passed node (UI only, internal)
     */
    async select(node) {
        if (!node) {
            this.#selector.val("");
            await this.#showGeneralParams();
        } else {
            this.#selector.val(node.id);
            await this.#showNode(node);
        }
    }

    /**
     * Updates the selected parameters from the data model
     */
    update() {
        // Parameters of selected node
        if (this.#parameterLists) {
            for (const list of this.#parameterLists) {
                list.update();
            }
        }
        
        // Selector
        this.#updateSelector();
    }

    /**
     * Shows parameters for the node
     */
    async #showNode(node) {
        await this.#setParameterLists(
            await node.type.getParameterLists()
        );
    }

    /**
     * Shows the general parameters
     */
    async #showGeneralParams() {
        await this.#setParameterLists([
            // General Params
            new DisplayGeneralParameterList(this.#editor),

            // Callback params
            new DisplayCallbackParameterList(
                this.#editor.controller,
                this.#editor.getConfig().parser,
                this.#editor.splashes,
                async function(param) {
                    return param.meta.visible()
                }
            )
        ]);
    }

    /**
     * Sets a list of ParameterList instances
     */
    async #setParameterLists(lists) {
        this.#parameterLists = lists;

        const content = [];
        for (const list of lists) {
            content.push(await list.get());
        }

        this.#parametersElement
            .empty()
            .append(
                content
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
                .text('General Attributes'),

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