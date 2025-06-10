/**
 * Parameters for display editor
 */
class DisplayParameters {
    
    #editor = null;
    container = null;

    #grid = null;

    constructor(editor) {
        this.#editor = editor;
    }

    async get() {
        return this.container = $('<div class="display-parameters-container" />');
    }

    async destroy() {        
        if (this.#grid) await this.#grid.destroy();
    }

    async init() {
        await this.#initGrid(this.container);
    }

    async clear() {
        // Clear
        this.container.empty();
    }

    /**
     * Init the grid (Muuri)
     */
    async #initGrid(gridElement) {
        // Init grid
        const that = this;
        this.#grid = new Muuri(gridElement[0], {
        /**
         * Drag options
         */
        dragEnabled: true,

//         // dragContainer: document.body,
//         // dragSort: function () {
//         //     return that.#parserFrontend.inputs
//         //         .filter((item) => !!item.#grid && item.definition.data.model.type == that.definition.data.model.type)
//         //         .map((item) => item.#grid);
//         // },
        
//         dragStartPredicate: function (item, e) {
//             // // Fix some items
//             // if ($(item.getElement()).find('.fixed').length > 0) return false;

//             if (e.deltaTime > 50 && e.distance > 20) {
//                 return Muuri.ItemDrag.defaultStartPredicate(item, e);
//             }
//         },

//         dragSortPredicate: function (item) {
//             const result = Muuri.ItemDrag.defaultSortPredicate(item, {
//                 action: 'swap',
//                 threshold: 50
//             });

//             // if (result) {
//                 // Get target item
//                 // const target = $(item.getElement()).parent().children().eq(result.index);
//                 // if (target.find('.fixed').length > 0) {
//                 //     return false;
//                 // }
//             // }

//             return result;
//         },

//         /**
//          * Custom layout
//          */
//         // layout: function (grid, layoutId, items, width, height, callback) {
//         //     const layout = {
//         //         id: layoutId,
//         //         items: items,
//         //         slots: [],
//         //         styles: {},
//         //     };

//         //     let y = 0;
//         //     let w = 0;
//         //     let h = 0;

//         //     for (let i = 0; i < items.length; ++i) {
//         //         const item = items[i];

//         //         y += h;
//         //         const m = item.getMargin();

//         //         const itemWidth = item.getWidth() + m.left + m.right;
//         //         if (itemWidth > w) w = itemWidth;
                
//         //         h = item.getHeight() + m.top + m.bottom;
                
//         //         layout.slots.push(0, y);
//         //     }

//         //     h += y;

//         //     // Set the CSS styles that should be applied
//         //     // to the grid element.
//         //     layout.styles.width = w + 'px';
//         //     layout.styles.height = h + 'px';

//         //     callback(layout);
//         // }
//     });

//     // // Grid events: On drag end we just schedule this grid for updating the config
//     // this.#grid.on('dragEnd', async function(item, event) {            
//     //     that.#parserFrontend.scheduleForUpdate(that);
//     // });

//     // // On release end (which is after dragEnd), we also schedule the input and trigger the update.
//     // this.#grid.on('dragReleaseEnd', async function(item, event) {
//     //     that.#parserFrontend.scheduleForUpdate(that);
        
//     //     // No await!
//     //     that.#parserFrontend.updateConfig();
        });          
    }
}