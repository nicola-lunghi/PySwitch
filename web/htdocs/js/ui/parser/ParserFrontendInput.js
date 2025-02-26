/**
 * Parser frontend for one input (shows actions for one input)
 */
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

        const that = this;

        const clients = await this.#parserFrontend.parser.getAvailableActions();

        function getActionDefinition(name, clientId) {
            for (const client of clients) {
                if (client.client != clientId) continue;

                for (const action of client.actions) {
                    if (action.name == name) return action;
                }
            }
            return null;
        }

        function getItemText(item) {
            const action = getActionDefinition(
                item.name, 
                item.client
            );
            
            if (!action) return item.name;
            
            return action.meta.getShortDisplayName({
                name: item.name,
                arguments: JSON.parse(item.arguments())
            });            
        }

        function getActionElements(a, buttonClass, hold, tooltip) {
            return a.map((item) =>
                $('<div class="action-item" />').append(
                    $('<div class="action-item-content" />')
                    .append(
                        // Action
                        $('<span class="button ' + buttonClass + ' name" data-toggle="tooltip" title="' + tooltip + '" />')
                        //.toggleClass("warn", item.)
                        .text(getItemText(item))
                        .on('click', async function() {
                            try {                                        
                                await that.promptEditAction(input, item, hold);

                            } catch (e) {
                                that.#controller.handle(e);
                            }
                        }),

                        // Remove button
                        $('<span class="button ' + buttonClass + ' remove-action fas fa-times" data-toggle="tooltip" title="Remove action" />')
                        .on('click', async function() {
                            try {
                                const action = $(this).parent().parent().data('handler');
                                
                                const inputName = input.display_name();        
                                if (!confirm("Do you want to delete " + action.name + " from " + inputName + "?")) {
                                    return;
                                }
                                                                              
                                await that.removeAction(input, action);

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
                                await that.promptAddAction(input);

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

        // Set the inputs accordingly (no update)
        await input.set_actions(newActions, false, true);
        await input.set_actions(newActionsHold, true, true);
    }

    /**
     * Shows the add action dialog
     */
    async promptAddAction(input) {
        const inputName = input.display_name();
        const that = this;

        const browser = await this.#promptAction(
            input,
            async function(action, hold) {
                await that.addAction(input, action, hold);
            },
            "Add an action to " + inputName,
            "Add"
        );

        browser.showInfoPanel("Please select an action to add");
    }

    /**
     * Shows the edit action dialog
     */
    async promptEditAction(input, action, hold) {
        const inputName = input.display_name();
        const that = this;

        const browser = await this.#promptAction(
            input,
            async function(actionNew, holdNew) {
                if (hold == holdNew) {
                    await that.replaceAction(input, action, actionNew);
                } else {
                    await that.removeAction(input, action);
                    await that.addAction(input, actionNew, holdNew);
                }                
            },
            "Edit/replace action \"" + action.name + "\" of " + inputName,
            "Apply",
            {
                name: action.name,
                arguments: JSON.parse(action.arguments()),
                hold: hold
            }
        );
    }

    /**
     * Shows the action edit/create dialog
     */
    async #promptAction(input, onCommit, headline, buttonText, preselectAction = null) {
        const that = this;

        let props = null;
        let actionsProvider = null;

        async function onSelect(entry) {
            props = new ActionProperties(
                entry.config.model,
                props
            );

            browser.showInfoPanel(await props.get());
            browser.setSelected(entry)
        }

        async function commit() {
            if (!props) {
                alert("Please select an action first");
                return;
            }

            const action = props.createActionDefinition();
            const hold = props.hold();

            await onCommit(action, hold);

            browser.hide();
        }

        // A browser to select client connections (to Kemper etc.), triggered by the client select button
        const browser = this.#controller.ui.getBrowserPopup({
            additionalClasses: "select-actions",
            headline: headline,
            wide: true,
            dontCloseOnSelect: true,
            onReturnKey: commit,
            providers: [
                actionsProvider = new ActionsProvider(
                    this.#parserFrontend.parser,
                    {
                        onSelect: onSelect,
                        preselectActionName: preselectAction ? preselectAction.name : null
                    }
                )
            ]
        });

        await browser.browse();

        if (preselectAction && actionsProvider.preselectEntry) {
            await onSelect(actionsProvider.preselectEntry);

            props.setArguments(preselectAction.arguments);
            props.setHold(preselectAction.hold)            
        }

        browser.setButtons(
            $('<div class="button" />')
            .text(buttonText)
            .on('click', async function() {
                try {
                    await commit();

                } catch(e) {
                    that.#controller.handle(e);
                }
            })
        );

        return browser;
    }

    /**
     * Adds an action to the passed input (proxy)
     */
    async addAction(input, actionDefinition, hold = false) {
        // Build actions definitions
        const newActions = this.#getItemHandlers(hold)
            .map((item) => { 
                return {
                    name: item.name,
                    client: item.client,
                    arguments: JSON.parse(item.arguments())
                }
            });
        
        // Add new action
        newActions.push(actionDefinition);
        
        // Update config
        const that = this;
        setTimeout(
            async function() {
                await input.set_actions(newActions, hold, true);

                await that.#parserFrontend.updateConfig();    
            }, 
            100
        );
    }

    /**
     * Replaces an action. 
     */
    async replaceAction(input, actionToReplace, actionDefinition) {
        const hold = this.#getHold(actionToReplace);

        const newActions = this.#getItemHandlers(hold)
            .map((item) => { 
                if (item == actionToReplace) return actionDefinition;

                return {
                    name: item.name,
                    client: item.client,
                    arguments: JSON.parse(item.arguments())
                }
            });
                
        // Update config
        const that = this;
        setTimeout(
            async function() {
                await input.set_actions(newActions, hold, true);

                await that.#parserFrontend.updateConfig();    
            }, 
            100
        );
    }
    
    /**
     * Removes an action from the passed input (proxy)
     */
    async removeAction(input, action) {
        const hold = this.#getHold(action);

        const newActions = this.#getItemHandlers(hold)
            .filter((item) => item != action)
            .map((item) => { 
                return {
                    name: item.name,
                    client: item.client,
                    arguments: JSON.parse(item.arguments())
                }
            });
                
        // Update config
        const that = this;
        setTimeout(
            async function() {
                await input.set_actions(newActions, hold, true);

                await that.#parserFrontend.updateConfig();    
            }, 
            100
        );
    }

    /**
     * Returns if the action is a hold action
     */
    #getHold(action) {
        const actions = this.#getItemHandlers(false);
        for (const a of actions) {
            if (a == action) return false;
        }

        const actionsHold = this.#getItemHandlers(true);
        for (const a of actionsHold) {
            if (a == action) return true;
        }

        throw new Error("Action not contained: " + action.name);
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