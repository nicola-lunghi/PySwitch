class PagesList {

    #grid = null;
    #gridElement = null;
    #controller = null;
    #onChange = null;

    // onChange is a change handler for inputs:
    // onChange(event) => void
    constructor(controller, onChange) {
        this.#controller = controller;
        this.#onChange = onChange;
    }

    /**
     * Returns the DOM for the pages list (empty by default). 
     */
    async create() {
        return $('<span class="pages-list-container" />').append(
            this.#gridElement = $('<div class="pages-grid" />')
        )
    }

    /**
     * Initialize the grid
     */
    async init() {
        await this.set(this.get())
    }

    /**
     * Sets the list from the passed pages list, and creates/refreshes the grid
     */
    async set(pages) {
        this.#gridElement.empty();
        
        const that = this;
        this.#gridElement.append(
            pages.map((item) => this.#createItem(item)),

            // Add page button
            $('<div class="page-item" />').append(
                $('<div class="page-item-content button add-page fixed fas fa-plus" data-toggle="tooltip" title="Add a page" />')                        
                .on('click', async function() {
                    try {
                        await that.#addPage();

                    } catch (e) {
                        that.#controller.handle(e);
                    }
                })
            )
        ); 
        
        await this.#initGrid();
        await this.#onChange();
    }

    /**
     * Create DOM for one page
     */
    #createItem(page) {
        const that = this;
        
        return $('<div class="page-item" />').append(
            $('<div class="page-item-content" />')
            .append(
                // Action
                $('<span class="button name" />')
                .append(
                    $('<input type="text" class="page-id" placeholder="Page ID" />')
                    .on('change', this.#onChange)
                    .val(page.id),

                    $('<input type="text" class="page-color" placeholder="Color (optional)" />')
                    .on('change', this.#onChange)
                    .val(page.color),

                    $('<input type="text" class="page-text" placeholder="Text (optional)" />')
                    .on('change', async function(e) {
                        $(this).val(Tools.autoQuote($(this).val()))

                        await that.#onChange(e);
                    })
                    .val(page.text)
                ),

                // Remove button
                $('<span class="button remove-page fas fa-times" data-toggle="tooltip" title="Remove page" />')
                .on('click', async function() {
                    try {
                        await that.#removePage(page.id);

                    } catch (e) {
                        that.#controller.handle(e);
                    }
                })
            )                    
        )
    }

    /**
     * Returns the pages list value
     */
    get() {
        if (!this.#grid) return [];
        const items = this.#grid.getItems();

        return items
            .filter((item) => !$(item.getElement()).find('.add-page').length)
            .map((item) => {
                const el = $(item.getElement());
                const ret = {
                    id: el.find('.page-id').val(),
                }

                const color = el.find('.page-color').val();
                if (color) {
                    ret.color = color;
                }

                const text = el.find('.page-text').val();
                if (text) {
                    ret.text = text;
                }

                return ret;
            });
    }

    /**
     * Add a new page
     */
    async #addPage() {
        const pages = await this.get();

        pages.push(
            {
                id: this.#getNextPageId(pages),
                color: "",
                text: ""
            }
        );

        await this.set(pages);
    }

    /**
     * Remove page by ID
     */
    async #removePage(id) {
        const pages = await this.get();

        await this.set(pages.filter((item) => item.id != id));
    }

    /**
     * Determines what the next page ID could be
     */
    #getNextPageId(pages) {
        let highest = -1;

        for(const page of pages) {
            const id = parseInt(page.id);
            if (id > highest) highest = id;
        }
        
        if (highest < 0) return "1";
        return "" + (highest + 1);
    }

    /**
     * Init the grid (Muuri)
     */
    async #initGrid() {
        // const that = this;
        
        if (this.#grid) {
            this.#grid.destroy();
        }

        if (!this.#gridElement) return;
        
        // Init grid        
        this.#grid = new Muuri(this.#gridElement[0], {
            /**
             * Drag options
             */
            dragEnabled: true,

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
    }
}