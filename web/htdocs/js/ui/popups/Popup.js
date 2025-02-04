class Popup {

    controller = null;
    element = null;
    
    #id = null;
    config = null;

    /**
     * config: {
     *      container:   Container DOM element (can be shared!)
     * }
     */
    constructor(controller, config) {
        this.controller = controller;
        this.config = config || {};

        this.element = this.config.container;
        
        this.#id = Tools.uuid();
    }

    /**
     * Hide: Remove all closing event handlers
     */
    hide() {
        this.controller.ui.progress(1);

        this.element.hide();
        this.element.empty();

        $(window).off('.' + this.#id);
        this.element.off('click.' + this.#id);
    }

    /**
     * Show the browser: Also adds some event handlers to close it on ESC and clicking outside
     */
    show(content, headline = null) {
        this.element.empty();

        this.element.append(
            $('<div class="content" />').append(
                // Headline
                !headline ? null :
                $('<div class="headline"/>')
                .text(headline),

                // Content
                $('<div class="user-content" />').append(
                    content
                ),

                // Close button
                $('<span class="fa fa-times close-button"/>')
                .on('click', async function() {
                    that.hide();
                })
            )
        );

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