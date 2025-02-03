class BrowserBase {

    element = null;
    controller = null;

    #id = null;

    constructor(controller, element) {
        this.controller = controller;
        this.element = element;

        this.#id = Tools.uuid();
    }

    hide() {
        this.controller.ui.progress(1);
        this.element.hide();

        $(window).off('.' + this.#id);
        this.element.off('click.' + this.#id);
    }

    show() {
        this.controller.ui.block();
        this.element.show();
        
        // ESC to close
        const that = this;
        $(window).on('keydown.' + this.#id, async function(event) {
            if(event.key === "Escape") {
                event.preventDefault();
                that.hide();
            }
        });

        this.element.on('click.' + this.#id, function(event) {
            event.stopPropagation();
        })

        setTimeout(function() {
            $(window).on('click.' + that.#id, async function() {
                that.hide();
            });    
        }, 0)
    }
}