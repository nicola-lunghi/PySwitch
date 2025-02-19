class ParserFrontendInput {

    #grid = null;

    #parserFrontend = null;
    #model = null;
    #inputElement = null;
    #gridElement = null;

    constructor(parserFrontend, model, inputElement) {
        this.#parserFrontend = parserFrontend;
        this.#model = model;
        this.#inputElement = inputElement;
    }

    async destroy() {
        if (this.#grid) await this.#grid.destroy();
    }

    /**
     * Adds the parser frontend for one input
     */
    async init() {
        // Parser UI
        const input = await this.#parserFrontend.parser.input(this.#model.port);
        if (!input) return;

        const actions = await input.actions();
        const actionsHold = await input.actions(true);
        const availableActions = await this.#parserFrontend.parser.getAvailableActions(this.#parserFrontend.basePath);
        
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

        this.#inputElement.append(
            $('<div class="pyswitch-parser-frontend" />').append(
                this.#gridElement = $('<div class="action-grid" />').append(
                    actions.map((item) =>
                        $('<div class="action-item" />').append(
                            $('<div class="action-item-content button actions" data-toggle="tooltip" title="Action on normal press" />')
                            .text(getItemText(item))
                        )
                        .data('handler', item)
                        .data('hold', false)
                    ),
                    actionsHold.map((item) =>
                        $('<div class="action-item" />').append(
                            $('<div class="action-item-content button actions-hold" data-toggle="tooltip" title="Action on long press" />')
                            .text(item.name)
                        )
                        .data('handler', item)
                        .data('hold', true)
                    )
                )
            )
        )

        // Init grid
        const that = this;
        this.#grid = new Muuri(this.#gridElement[0], {
            /**
             * Drag options
             */
            dragEnabled: true,

            // dragContainer: document.body,

            dragSort: function () {
                return that.#parserFrontend.inputs.map((item) => item.#grid);
            },
            
            dragStartPredicate: {
                distance: 20,
                delay: 50
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

            // that.#grid.synchronize();
        });

        // On release end (which is after dragEnd), we also schedule the input and trigger the update.
        this.#grid.on('dragReleaseEnd', async function(item, event) {
            that.#parserFrontend.scheduleForUpdate(that);

            // that.#grid.synchronize();            
            
            // No await!
            that.#parserFrontend.updateConfig();
        });          
    }

    /**
     * Updates the parser data model from the current state
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
     * Returns the item handlers in the correct order
     */
    #getItemHandlers(hold) {
        const items = this.#grid.getItems();

        return items
            .filter((item) => $(item.getElement()).data('hold') == hold)
            .map((item) => $(item.getElement()).data('handler'));
    }
}