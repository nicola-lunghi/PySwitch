class BrowserBase {

    element = null;
    #id = null;
    #hideOnEscapeOrClickOutside = null;

    constructor(element, hideOnEscapeOrClickOutside = true) {
        this.element = element;
        this.#id = Tools.uuid();
        this.#hideOnEscapeOrClickOutside = hideOnEscapeOrClickOutside;
    }

    hide() {
        this.element.hide();

        $(window).off('.' + this.#id);
        this.element.off('click.' + this.#id);
    }

    show() {
        this.element.show();
        
        if (this.#hideOnEscapeOrClickOutside) {
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
                $(window).on('click.' + that.#id, async function(event) {
                    that.hide();
                });    
            }, 0)
        }
    }
}