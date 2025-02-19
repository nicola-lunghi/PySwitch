class ParserFrontend {

    #grid = null;
    #pyswitchFrontent = null;

    constructor(pyswitchFrontent) {
        this.#pyswitchFrontent = pyswitchFrontent;
    }

    /**
     * Adds the parser frontend for one input
     */
    async init(parser, model, inputElement) {
        if (!inputElement) return;
        
        // Parser UI
        const input = await parser.input(model.port);
        if (!input) return;

        const actions = await input.actions();
        const actionsHold = await input.actions(true);
        
        let gridElement = null;

        inputElement.append(
            $('<div class="pyswitch-parser-frontend" />').append(
                gridElement = $('<div class="action-grid" />').append(
                    actions.map((item) =>
                        $('<div class="action-item" />').append(
                            $('<div class="action-item-content button actions" data-toggle="tooltip" title="Action on normal press" />')
                            .text(item.name)
                        )
                    ),
                    actionsHold.map((item) =>
                        $('<div class="action-item" />').append(
                            $('<div class="action-item-content button actions-hold" data-toggle="tooltip" title="Action on long press" />')
                            .text(item.name)
                        )
                    )
                )
            )
        )

        // Init grid
        const that = this;
        this.#grid = new Muuri(gridElement[0], {
            dragEnabled: true,
            // dragContainer: document.body,
            dragSort: function () {
                return that.#pyswitchFrontent.parserFrontends.map((item) => item.#grid);
            },
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

        // Grid events
        this.#grid.on('dragReleaseEnd', async function(item, event) {
            console.log(that.#grid.getItems())
        });
        this.#grid.on('dragEnd', async function(item, event) {
            console.log(that.#grid.getItems())
        });
    }
}