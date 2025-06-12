/**
 * Generic popup
 */
class Popup {

    element = null;        // Content element
    #container = null;  
    options = null;

    #id = null;            // Only used for handlers

    /**
     * {
     *      container:                Container DOM element. Will be hidden/shown along with the popups.
     *      additionalClasses:        Optional CSS classes for the popup element
     *      onReturnKey:              Callback when the user hits the Return key
     *      buttons: [                Optional buttons
     *          {
     *              text: 
     *              onClick: async function() {}
     *          }
     *      ],
     *      onClose:                  Called on hide (not awaited!)
     *      confirmClose:             If given and returns false, closing will be exited. (not awaited!)
     *      errorHandler:             Optional error handler. must provide a handle(ex) => void method.
     * }
     */
    constructor(options) {
        this.options = options || {};

        this.#id = Tools.uuid();
    }

    /**
     * Hide: Remove all closing event handlers
     */
    hide(noCallback = false) {
        if (this.#container) {
            this.#container.remove();
        }        

        this.options.container.hide();

        this.#container = null;
        this.element = null;
        
        $(window).off('.' + this.#id);

        if (!noCallback && this.options.onClose) {
            this.options.onClose();
        }
    }

    /**
     * Show the browser: Also adds some event handlers to close it on ESC and clicking outside
     */
    show(content, headline = null) {
        this.hide(true);

        const that = this;
        function confirmAndHide() {
            if (that.options.confirmClose) {
                if (!that.options.confirmClose()) return;
            }
            that.hide();
        }

        this.options.container.append(
            this.#container = $('<div class="list-block" />').append(
                this.element = $('<div class="list-browser"/>')
                    .toggleClass("wide", !!this.options.wide)
                    .toggleClass("fullscreen", !!this.options.fullscreen)                    
                    .append(
                        $('<div class="content" />')
                        .append(
                            // Headline
                            !headline ? null :
                            $('<div class="headline"/>')
                            .text(headline)
                        )
                        .append(            
                            // Content
                            content
                        )
                        .append(
                            this.#generateButtons()
                        )
                        .append(                            
                            // Close button
                            $('<span class="fa fa-times close-button"/>')
                            .on('click', function() {
                                confirmAndHide();
                            })
                        )
                    )
            )
        );

        if (this.options.additionalClasses) {
            this.element.addClass(this.options.additionalClasses);
        }

        // ESC to close
        $(window).on('keydown.' + this.#id, async function(event) {
            if (event.key === "Escape") {
                event.preventDefault();
                confirmAndHide();
            }
            
            if (event.key === "Enter") {
                if (that.options.onReturnKey) {
                    await that.options.onReturnKey();
                }
            }
        });

        this.element.on('click.' + this.#id, function(event) {
            event.stopPropagation();
        })

        this.options.container.show();

        setTimeout(function() {
            $(window).on('click.' + that.#id, async function() {
                confirmAndHide();
            });    
        }, 0)
    }

    /**
     * Error handling
     */
    handle(e) {
        if (this.options.errorHandler) {
            this.options.errorHandler.handle(e);
            return;
        }

        console.error(e);
    }

    #generateButtons() {
        if (!this.options.buttons) return null;

        const that = this;

        return $('<div class="buttons" />').append(
            this.options.buttons.map((el) => {
                return $('<div class="button" />')
                    .text(el.text)
                    .on('click', async function() {
                        try {
                            await el.onClick();
        
                        } catch(e) {
                            that.handle(e);
                        }
                    })
            })
        )
    }
}