class ParserFrontendInput {

    #grid = null;
    #controller = null;
    #parserFrontend = null;
    #model = null;
    #inputElement = null;
    #gridElement = null;

    constructor(controller, parserFrontend, model, inputElement) {
        this.#controller = controller;
        this.#parserFrontend = parserFrontend;
        this.#model = model;
        this.#inputElement = inputElement;
    }

    /**
     * Destroy the input
     */
    async destroy() {
        if (this.#grid) await this.#grid.destroy();
    }

    /**
     * Adds the parser frontend for one input
     */
    async init() {
        await this.#initDom();
        await this.#initGrid();
    }

    /**
     * Init the UI
     */
    async #initDom() {
        // Parser UI
        const input = await this.#parserFrontend.parser.input(this.#model.port);
        if (!input) return;

        const actions = await input.actions();
        const actionsHold = await input.actions(true);
        const availableActions = await this.#parserFrontend.parser.getAvailableActions(this.#parserFrontend.basePath);
        
        const that = this;

        function getActionDefinition(name) {
            for (const action of availableActions) {
                if (action.name == name) {
                    return action
                }
            }
            return null;
        }

        function getItemText(item) {
            const definition = getActionDefinition(item.name);
            if (!definition) return item.name;
            
            const meta = new Meta(definition);
            return meta.getDisplayName({
                name: item.name,
                arguments: JSON.parse(item.arguments())
            });            
        }

        function getActionElements(a, buttonClass, hold, tooltip) {
            return a.map((item) =>
                $('<div class="action-item" />').append(
                    $('<div class="action-item-content" />')
                    .append(
                        $('<span class="button ' + buttonClass + ' name" data-toggle="tooltip" title="' + tooltip + '" />')
                        .text(getItemText(item)),

                        $('<span class="button ' + buttonClass + ' remove-action fas fa-times" data-toggle="tooltip" title="Remove action" />')
                        .on('click', async function() {
                            try {                                        
                                await that.removeAction(input, $(this).parent().parent());

                            } catch (e) {
                                that.#controller.handle(e);
                            }
                        })
                    )                    
                )
                .data('handler', item)
                .data('hold', hold)
            )
        }

        this.#inputElement.append(
            $('<div class="pyswitch-parser-frontend" />').append(                
                this.#gridElement = $('<div class="action-grid" />').append(
                    // Actions
                    getActionElements(
                        actions,
                        "actions",
                        false,
                        "Action on normal press"
                    ),

                    // Hold actions
                    getActionElements(
                        actionsHold,
                        "actions-hold",
                        true,
                        "Action on long press"
                    ),

                    // Add action button
                    $('<div class="action-item" />').append(
                        $('<div class="action-item-content button actions add-action fixed fas fa-plus" data-toggle="tooltip" title="Add an action" />')                        
                        .on('click', async function() {
                            try {
                                await that.addAction(input);

                            } catch (e) {
                                that.#controller.handle(e);
                            }
                        })
                    )
                )
            )
        )
    }

    /**
     * Init the grid (Muuri)
     */
    async #initGrid() {
        if (!this.#gridElement) return;
        
        // Init grid
        const that = this;
        this.#grid = new Muuri(this.#gridElement[0], {
            /**
             * Drag options
             */
            dragEnabled: true,

            // dragContainer: document.body,

            dragSort: function () {
                return that.#parserFrontend.inputs.filter((item) => !!item.#grid).map((item) => item.#grid);
            },
            
            dragStartPredicate: function (item, e) {
                // Fix some items
                if ($(item.getElement()).find('.fixed').length > 0) return false;

                if (e.deltaTime > 50 && e.distance > 20) {
                    return Muuri.ItemDrag.defaultStartPredicate(item, e);
                }
            },

            dragSortPredicate: function (item) {
                const result = Muuri.ItemDrag.defaultSortPredicate(item, {
                    action: 'swap',
                    threshold: 50
                });

                if (result) {
                    // Get target item
                    const target = $(item.getElement()).parent().children().eq(result.index);
                    if (target.find('.fixed').length > 0) {
                        return false;
                    }
                }

                return result;
            },

            /**
             * Custom layout
             */
            layout: function (grid, layoutId, items, width, height, callback) {
                const layout = {
                    id: layoutId,
                    items: items,
                    slots: [],
                    styles: {},
                };

                let y = 0;
                let w = 0;
                let h = 0;

                for (let i = 0; i < items.length; ++i) {
                    const item = items[i];

                    y += h;
                    const m = item.getMargin();

                    const itemWidth = item.getWidth() + m.left + m.right;
                    if (itemWidth > w) w = itemWidth;
                    
                    h = item.getHeight() + m.top + m.bottom;
                 
                    // if ($(item.getElement()).find('.fixed').length > 0) {
                    //     // TODO align fixed items to the right
                    // }

                    layout.slots.push(0, y);
                }

                h += y;

                // Set the CSS styles that should be applied
                // to the grid element.
                layout.styles.width = w + 'px';
                layout.styles.height = h + 'px';

                callback(layout);
            }
        });

        // Grid events: On drag end we just schedule this grid for updating the config
        this.#grid.on('dragEnd', async function(item, event) {            
            that.#parserFrontend.scheduleForUpdate(that);
        });

        // On release end (which is after dragEnd), we also schedule the input and trigger the update.
        this.#grid.on('dragReleaseEnd', async function(item, event) {
            that.#parserFrontend.scheduleForUpdate(that);
            
            // No await!
            that.#parserFrontend.updateConfig();
        });          
    }

    /**
     * Updates the parser data model from the current DOM state
     */
    async updateInput() {
        const input = await this.#parserFrontend.parser.input(this.#model.port);
        if (!input) throw new Error("Input not found for port " + this.#model.port);

        // Build actions definitions
        const newActions = this.#getItemHandlers(false)
            .map((item) => { return {
                name: item.name,
                arguments: JSON.parse(item.arguments())
            }});

        const newActionsHold = this.#getItemHandlers(true)
            .map((item) => { return {
                name: item.name,
                arguments: JSON.parse(item.arguments())
            }});

        // console.log(newActions)
        // console.log(newActionsHold)

        // Set the inputs accordingly (no update)
        await input.set_actions(newActions, false, true);
        await input.set_actions(newActionsHold, true, true);
    }

    /**
     * Adds an action to the passed input (proxy)
     */
    async addAction(input) {
        const that = this;

        const inputName = input.display_name();

        // A browser to select client connections (to Kemper etc.), triggered by the client select button
        const browser = this.#controller.ui.getBrowserPopup({
            headline: "Please select an action to add to " + inputName,
            wide: true,
            providers: [
                
            ],
            // postProcess: function(entry, generatedElement) {
            //     // Highlight currently selected client
            //     const client = that.#controller.getState("client");

            //     if (client == entry.value) {
            //         generatedElement.addClass('highlighted');
            //     }
            // }
        });

        await browser.browse();
    }

    /**
     * Removes an action from the passed input (proxy)
     */
    async removeAction(input, itemElement) {
        const inputName = input.display_name();
        
        if (!confirm("Do you want to delete the action from " + inputName + "?")) {
            this.#controller.ui.message("Action canceled", "I")
            return;
        }

        const muuriItem = this.#grid.getItem(itemElement[0]);
        if (!muuriItem) throw new Error("Item not found")

        this.#grid.remove(
            [muuriItem], 
            { 
                removeElements: true 
            }
        );
        
        const that = this;
        setTimeout(
            async function() {
                await that.updateInput();
                await that.#parserFrontend.updateConfig();    
            }, 
            100
        );
    }

    /**
     * Returns the item handlers in the correct order
     */
    #getItemHandlers(hold) {
        const items = this.#grid.getItems();

        return items
            .filter((item) => $(item.getElement()).data('hold') == hold)
            .map((item) => $(item.getElement()).data('handler'));
    }
}