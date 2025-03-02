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
     *      onClose:                  Called on hide
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
    hide() {
        if (this.#container) {
            this.#container.remove();
        }        

        this.options.container.hide();

        this.#container = null;
        this.element = null;
        
        $(window).off('.' + this.#id);
    }

    /**
     * Show the browser: Also adds some event handlers to close it on ESC and clicking outside
     */
    show(content, headline = null) {
        this.hide();

        this.options.container.append(
            this.#container = $('<div class="list-block" />').append(
                this.element = $('<div class="list-browser"/>')
                    .toggleClass("wide", !!this.options.wide)
                    .toggleClass("fullscreen", !!this.options.fullscreen)                    
                    .append(
                        $('<div class="content" />').append(
                            // Headline
                            !headline ? null :
                            $('<div class="headline"/>')
                            .text(headline),
            
                            // Content
                            content,
                            
                            // Close button
                            $('<span class="fa fa-times close-button"/>')
                            .on('click', async function() {
                                if (that.options.onClose) {
                                    await that.options.onClose();
                                }
                        
                                that.hide();
                            })
                        )
                    )
            )
        );

        if (this.options.additionalClasses) {
            this.element.addClass(this.options.additionalClasses);
        }

        // ESC to close
        const that = this;
        $(window).on('keydown.' + this.#id, async function(event) {
            if (event.key === "Escape") {
                event.preventDefault();
                that.hide();
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
                that.hide();
            });    
        }, 0)
    }
}